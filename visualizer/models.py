from __future__ import unicode_literals

import io
import os

from django.db import models


class AudioFragment(models.Model):
    """An AudioFragment is a segment of an audio Document that may be (but
    is not necessarily) associated with a Term
    """
    # { "_id" : ObjectId("55e5b895841fd54738fd3bc5"), "zr_pt_id" : 168, "start_offset" : 8534, "pt_id" : ObjectId("55e5b892841fd54738fcf338"), "utterance_id" : ObjectId("55e5b894841fd54738fd3172"), "time" : 1441118357000, "duration" : 54, "end_offset" : 8588 }
    document = models.ForeignKey('Document')
    term = models.ForeignKey('Term')

    # Index generated by ZRTools for this audio fragment  (Old name for this variable was 'zr_pt_id')
    zr_fragment_index = models.IntegerField()

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

    def create_from_zr_output(self, corpus_name, audiofragments, clusters, filenames, \
                              audio_rate, audio_channels, audio_precision):
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

        self.name = corpus_name

        # Assumption: All audio files in the corpus have same audio characteristics
        self.audio_rate = audio_rate
        self.audio_channels = audio_channels
        self.audio_precision = audio_precision

        self.save()

        # The 'filenames' file is a text file listing the paths the audio Documents:
        #   /Users/charman/zr_datasets/BUCKEYE/s38/s3802a.wav
        #   /Users/charman/zr_datasets/BUCKEYE/s38/s3802b.wav
        document_for_audio_identifier = {}
        full_filenames = _slurp(filenames)
        for (document_index, full_filename) in enumerate(full_filenames):
            basename = os.path.splitext(os.path.basename(full_filename))[0]

            document = Document()
            document.corpus = self
            document.document_index = document_index
            document.audio_identifier = basename
            document.audio_path = full_filename.strip()
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
            term.eng_display = 'pt%d' % term_index
            term.native_display = 'PT%d' % term_index
            term.zr_pt_id = term_index
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

    def terms(self):
        return Term.objects.filter(audiofragment__document__corpus=self).distinct()

class Document(models.Model):
    """An audio Document associated with an audio file
    """
    # The 'utterance' MongoDB field has been renamed 'Document'
    # { "_id" : ObjectId("55e5b893841fd54738fcfdec"), "utterance_index" : 19, "hltcoe_audio_path" : "/Users/charman/zr_datasets/BUCKEYE/s36/s3603b.wav", "audio_identifier" : "s3603b", "pts" : [ ObjectId("55e5b893841fd54738fcfded"), ObjectId("55e5b893841fd54738fcfdee"), ObjectId("55e5b893841fd54738fcfdee") ] }
    corpus = models.ForeignKey(Corpus)

    # The document_index is a zero-based document counter
    document_index = models.IntegerField()

    audio_path = models.TextField()
    audio_identifier = models.TextField()

    def associated_terms(self):
        return Term.objects.filter(audiofragment__document=self).distinct()

class Term(models.Model):
    """
    """
    # { "_id" : ObjectId("55e5b892841fd54738fcf337"), "eng_display" : "pt159", "native_display" : "PT159", "zr_pt_id" : 159 }
    eng_display = models.TextField()
    native_display = models.TextField()

    # Term index generated by the ZRTools code
    zr_pt_id = models.IntegerField()

    def audio_fragment_ids(self):
        return self.audiofragment_set.values_list('id', flat=True)

    def total_audio_fragments(self):
        return self.audiofragment_set.count()

    def document_ids(self):
        return self.audiofragment_set.values_list('document__id', flat=True).distinct()

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
