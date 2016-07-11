from __future__ import unicode_literals

import io
import logging
import os
import os.path

from django.db import connection, models
from django.db.models import Sum
import pysox


class AudioFragment(models.Model):
    """An AudioFragment is a segment of an audio Document that may be (but
    is not necessarily) associated with a Term
    """
    document = models.ForeignKey('Document')
    term = models.ForeignKey('Term')

    # Index generated by ZRTools for this audio fragment  (Old name for this variable was 'zr_pt_id')
    zr_fragment_index = models.IntegerField()

    # offsets and duration are measured in hundredths of a second
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()
    duration = models.IntegerField()

    score = models.FloatField()

class Corpus(models.Model):
    """
    """
    name = models.TextField()
    audio_rate = models.IntegerField()
    audio_channels = models.IntegerField()
    audio_precision = models.IntegerField()

    protected_corpus = models.BooleanField(default=False)

    OBJECTS_PER_BULK_OPERATION = 1000

    def __unicode__(self):
        return self.name

    def create_from_ctm_file(self, corpus_name, ctm_file_path, audio_directory, audio_extension,
                             protect_corpus=False):
        """Create a corpus from a CTM file and associated audio files
        """
        # When using SQLite on a hard disk, disabling synchronous writes
        # on corpus creation increases ingest speed by up to x50.
        if connection.vendor == u'sqlite':
            cursor = connection.cursor()
            cursor.execute('PRAGMA synchronous=OFF;')

        self.name = corpus_name

        self.protected_corpus = protect_corpus

        ctm_file = open(ctm_file_path, "r")

        document_for_audio_identifier = {}
        term_for_keyword = {}
        zr_fragment_index = 0

        audio_fragments_for_bulk_commit = []

        for line in ctm_file:
            if not line.strip():
                # Ignore blank lines
                continue
            if line.strip()[0:2] == ';;':
                # Ignore comments
                continue
            fields = line.split()
            if len(fields) != 5 and len(fields) != 6:
                logging.warning("Expected line of CTM file to have 5 or 6 fields, but found %d fields. Line: '%s'" % \
                                (len(fields), line.split()))
            audio_identifier = fields[0]
            start_offset = int(float(fields[2]) * 100)
            duration = int(float(fields[3]) * 100)
            keyword = fields[4]
            audio_path = os.path.join(audio_directory, audio_identifier + "." + audio_extension)
            if not os.path.isfile(audio_path):
                logging.warning("Unable to find audio file with path '%s'" % audio_path)

            if not audio_identifier in document_for_audio_identifier:
                # Set Corpus audio signal info from the first audio document
                if len(document_for_audio_identifier) == 0:
                    audio = pysox.CSoxStream(audio_path)
                    signal_info = audio.get_signal().get_signalinfo()
                    self.audio_rate = signal_info['rate']
                    self.audio_channels = signal_info['channels']
                    self.audio_precision = signal_info['precision']
                    self.save()

                document = Document()
                document.corpus = self
                document.document_index = len(document_for_audio_identifier)
                document.audio_path = audio_path
                document.audio_identifier = audio_identifier

                if os.path.isfile(document.audio_path):
                    si = pysox.CSoxStream(document.audio_path).get_signal().get_signalinfo()
                    length_in_seconds = si['length'] / float(self.audio_rate * self.audio_channels)
                    document.duration = int(length_in_seconds * 100)
                else:
                    document.duration = 0
                    logging.warning("Unable to find audio file with path '%s'" % document.audio_path)

                document.save()
                document_for_audio_identifier[document.audio_identifier] = document
            else:
                document = document_for_audio_identifier[audio_identifier]

            if not keyword in term_for_keyword:
                term = Term()
                term.label = keyword
                term.zr_term_index = len(term_for_keyword)
                term.save()
                term_for_keyword[keyword] = term
            else:
                term = term_for_keyword[keyword]

            audio_fragment = AudioFragment()
            audio_fragment.document = document
            audio_fragment.term = term
            audio_fragment.zr_fragment_index = zr_fragment_index
            audio_fragment.start_offset = start_offset
            audio_fragment.end_offset = start_offset + duration
            audio_fragment.duration = duration
            audio_fragment.score = 0

            zr_fragment_index += 1

            audio_fragments_for_bulk_commit.append(audio_fragment)
            if len(audio_fragments_for_bulk_commit) % Corpus.OBJECTS_PER_BULK_OPERATION == 0:
                AudioFragment.objects.bulk_create(audio_fragments_for_bulk_commit)
                audio_fragments_for_bulk_commit = []

        AudioFragment.objects.bulk_create(audio_fragments_for_bulk_commit)
        ctm_file.close()

    def create_from_zr_output(self, corpus_name, audiofragments, clusters, filenames,
                              audio_rate, audio_channels, audio_precision,
                              audio_directory=None, audio_extension=None,
                              protect_corpus=False):
        """
        """
        # "Documentation" from Aren via Glen
        #
        #   matches/master_graph.nodes   - node file
        #   matches/master_graph.dedups  - deduped cluster file
        #   matches/master_graph.feats   - hard PT counts
        #   fileswav.lst                 - filenames of wav files
        #
        # formats (divide frames by 100 to get seconds):
        #
        #   nodes: file start_frame end_frame score ignore ignore
        #   dedups: one line per PT cluster, containing list of node ids
        #           (correspond to nodes line #s)
        #   feats: one line per cut, list of (PTID,count) pairs, where PTID is the line # in dedups file

        # When using SQLite on a hard disk, disabling synchronous writes
        # on corpus creation increases ingest speed by up to x50.
        if connection.vendor == u'sqlite':
            cursor = connection.cursor()
            cursor.execute('PRAGMA synchronous=OFF;')

        self.name = corpus_name

        # Assumption: All audio files in the corpus have same audio characteristics
        self.audio_rate = audio_rate
        self.audio_channels = audio_channels
        self.audio_precision = audio_precision

        self.protected_corpus = protect_corpus

        self.save()

        # The 'filenames' file is a text file listing the paths the audio Documents:
        #   /Users/charman/zr_datasets/BUCKEYE/s38/s3802a.wav
        #   /Users/charman/zr_datasets/BUCKEYE/s38/s3802b.wav
        document_for_audio_identifier = {}
        full_filenames = _slurp(filenames)
        for (document_index, full_filename) in enumerate(full_filenames):
            basename = os.path.splitext(os.path.basename(full_filename))[0].strip()

            document = Document()
            document.corpus = self
            document.document_index = document_index
            document.audio_identifier = basename
            if audio_directory:
                document.audio_path = os.path.join(audio_directory, os.path.basename(full_filename)).strip()
            else:
                document.audio_path = full_filename.strip()
            if audio_extension:
                document.audio_path += "." + audio_extension

            if os.path.isfile(document.audio_path):
                si = pysox.CSoxStream(document.audio_path).get_signal().get_signalinfo()
                length_in_seconds = si['length'] / float(audio_rate * audio_channels)
                document.duration = int(length_in_seconds * 100)
                if document.duration == 0:
                    logging.warning("Audio file '%s' has length 0" % document.audio_path)
            else:
                document.duration = 0
                logging.warning("Unable to find audio file with path '%s'" % document.audio_path)

            document.save()

            document_for_audio_identifier[document.audio_identifier] = document

        # The 'clusters' file is a text file, where each line of the file
        # specifies the AudioFragments for a Term.  AudioFragments are
        # identified by the line number in the audiofragments file, where
        # the first line of the file is 0 and *not* 1:
        #   13 14
        #   15 16 51 52
        #   17 18 30855 30856 68607 68608 130351 130352 164607 164608 164611 164612
        cluster_lines = _slurp(clusters)
        term_for_audio_fragment_index = {}
        for (term_index, cluster_line) in enumerate(cluster_lines):
            term = Term()
            term.label = ''
            term.zr_term_index = term_index
            term.save()
            for audio_fragment_index in cluster_line.split():
                # TODO: Verify that audio_fragment_index hasn't been associated with another term
                term_for_audio_fragment_index[int(audio_fragment_index)] = term

        # The 'audiofragments' file is a TSV file with six fields:
        #   s3802b  55028   55087   0.911181        23.175030       896
        #   s3802b  55085   55144   0.911181        23.175030       896
        fragment_lines = _slurp(audiofragments)
        for (audio_fragment_index, line) in enumerate(fragment_lines, start=1):
            # Only create AudioFragment instance for fragments associated with a Term
            if audio_fragment_index in term_for_audio_fragment_index:
                (audio_identifier, start, end, score, ignore1, ignore2) = line.split();
                audio_fragment = AudioFragment()
                audio_fragment.document = document_for_audio_identifier[audio_identifier]
                audio_fragment.term = term_for_audio_fragment_index[audio_fragment_index]
                audio_fragment.zr_fragment_index = audio_fragment_index
                audio_fragment.start_offset = int(start)
                audio_fragment.end_offset = int(end)
                audio_fragment.duration = audio_fragment.end_offset - audio_fragment.start_offset
                audio_fragment.score = score
                audio_fragment.save()

    def duration_as_hh_mm_ss(self):
        m, s = divmod(self.duration_in_seconds(), 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    def duration_in_seconds(self):
        h = Corpus.objects.filter(id=self.id).aggregate(Sum('document__duration'))
        return h['document__duration__sum'] / 100.0

    def terms(self):
        return Term.objects.filter(audiofragment__document__corpus=self).distinct()

    def total_audio_fragments(self):
        return AudioFragment.objects.filter(document__corpus=self).distinct().count()

    def total_terms(self):
        return self.terms().count()

class Document(models.Model):
    """An audio Document associated with an audio file
    """
    corpus = models.ForeignKey(Corpus)

    # The document_index is a zero-based document counter
    document_index = models.IntegerField()

    audio_path = models.TextField()
    audio_identifier = models.TextField()

    # duration is measured in hundredths of a second
    duration = models.IntegerField()

    def associated_terms(self):
        return Term.objects.filter(audiofragment__document=self).distinct()

    def duration_in_seconds(self):
        return self.duration / 100.0

    def total_terms(self):
        return Term.objects.filter(audiofragment__document=self).distinct().count()


class DocumentTopic(models.Model):
    """
    """
    label = models.TextField()
    corpus = models.ForeignKey(Corpus)
    documents = models.ManyToManyField(Document)


class Term(models.Model):
    """
    """
    label = models.TextField()

    # Term index generated by the ZRTools code
    zr_term_index = models.IntegerField()

    updated_at = models.DateField(auto_now=True)

    def audio_fragment_ids(self):
        return self.audiofragment_set.values_list('id', flat=True)

    def corpus_id(self):
        # Assumes that all audio fragments for this term belong to the same corpus
        return self.audiofragment_set.first().document.corpus.id

    def document_ids(self):
        return self.audiofragment_set.values_list('document__id', flat=True).distinct()

    def first_start_offset_in_document(self, doc):
        af = self.audiofragment_set.filter(document=doc).order_by('start_offset').first()
        if af:
            # Start offset is returned in seconds
            return af.start_offset / 100.0
        else:
            return None

    def total_audio_fragments(self):
        return self.audiofragment_set.count()

    def total_audio_fragments_in_document(self, doc):
        return self.audiofragment_set.filter(document=doc).count()

    def total_documents(self):
        return Document.objects.filter(audiofragment__term=self).distinct().count()


def _slurp(fname, encoding='utf-8'):
    # Some of the source files have the unicode characters \u2028
    # (line separator) and \u2029 (paragraph separator)
    ## NB: io.open ignores \u2028 and \u2029 (thankfully), while codecs.open() does not
    f = io.open(fname, 'r', encoding=encoding, newline='\n')

    lines = []
    try:
        lines = f.readlines()
    finally:
        f.close()
    return lines
