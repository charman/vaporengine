# Python standard library modules
import argparse
import datetime as dt
import os
import tempfile

# Third party modules
from bottle import HTTPResponse, route, run, request, response, static_file, template, TEMPLATE_PATH
from bson import ObjectId
import bson.json_util
import pysox
try:
    import ujson as json
except:
    import json

# Local modules
from lib.database import init_dbconn
from lib.queries import (find_annotations, find_utterances,
                         find_pseudoterms, find_audio_events,
                         pseudoterm_is_junk,
                         update_pseudoterm)
from settings import current_corpora, settings
from vapor_venncloud import make_wc_datastructure


vaporviz_path = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_PATH.append(os.path.join(vaporviz_path, 'page_source'))


"""Decorator that enables Cross-Origin Resource Sharing (CORS)"""
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

"""Decorator that returns HTTP response as JSON"""
def json_wrapper(method):
    def rapper(*a, **kw):
        resp = method(*a, **kw)
        response.content_type = 'application/json'

        # bson.json_util.dumps() knows how to convert Mongo ObjectId's to JSON
        return bson.json_util.dumps(resp)
    return rapper


def bytestring_as_file_with_mimetype(bytestring, mimetype):
    """
    Based on static_file() in bottle.py
    """
    headers = dict()
    headers['Content-Length'] = len(bytestring)
    headers['Content-Type'] = mimetype
    return HTTPResponse(bytestring, **headers)


"""For serving generic widgets and pages"""
@route('/www/<path>')
def widget_handler(path):
    source_path = 'page_source/%s' % path
    try:
        page = open( source_path ).read()
    except:
        #print "Failing to find", source_path
        source_path = 'vaporviz/'+source_path
        #print "Looking for", source_path
        page = open( source_path ) .read()
    print "Returning what was found at:", source_path
    return page


"""
For serving CSS

static_file returns the CSS files with mime-type "text/css", while the
"/www/<path>" route implemented by widget_handler() will return CSS files
with mime-type "text/html".  Chrome 35, Firefox 30 and Safari 7 will not
use CSS rules in a file if the file's mime-type is "text/html".
"""
@route('/css/<filepath:path>')
def css_handler(filepath):
    vaporviz_path = os.path.dirname(os.path.realpath(__file__))
    return static_file(filepath, root=os.path.join(vaporviz_path, 'page_source'))


"""For serving up pages that must be corpus aware"""
@route('/corpus/<corpus_name>/<page_path>')
def corpus_aware_handler(corpus_name,page_path):
    source_path = 'page_source/%s' % page_path
    try:
        print "Returning what was found at:", source_path
        return template(source_path, corpus_name=corpus_name)
    except:
        source_path = 'vaporviz/'+source_path
        print "Failing, trying  what was found at:", source_path
        return template(source_path, corpus_name=corpus_name)


@route('/static/<filepath:path>')
def static_files(filepath):
    vaporviz_path = os.path.dirname(os.path.realpath(__file__))
    return static_file(filepath, root=os.path.join(vaporviz_path, 'static'))


def generic_find(find_function, metadata_filters):
    """Does all the requisite conversions for pulling from the database
    and preparing to serve to the website.
    `find_function` should be one of the function from queries.py"""
    print metadata_filters
    dataset_name = metadata_filters['dataset'] #This maps to MongoDB table name
    print "from dataset:", dataset_name
    del metadata_filters['dataset']

    #SECURITY add whitelist of dataset names permitted
    db = init_dbconn(name=settings[dataset_name]['DB_NAME'], host=settings[dataset_name]['DB_HOST'])

    #Properly Cast count
    if 'count' in metadata_filters:
        try:
            metadata_filters['count'] = int(metadata_filters['count'])
        except:
            metadata_filters['count'] = 0

    #SECURITY -- delete all keys not in a whitelisted set of keys

    sort_by = [('time',-1)]
    if 'sort_by' in metadata_filters:
        sort_by = metadata_filters['sort_by'] #Or do we need a conversion here

    print metadata_filters
    cursor = find_function(db, **metadata_filters)

    #Accumulate results
    results = []
    for result in cursor:
        #stringify mongoIDs (bson ids) before we pass it on
        result['_id'] = str(result['_id'])
        for bson_id_type in ['pt_id','utterance_id']:
            if bson_id_type in result:
                result[bson_id_type] = str(result[bson_id_type])
        results.append(result)
    print "Results:", results
    return results

@route('/find_annotations',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def find_annotations_handler():
    metadata_filters = json.load(request.body)
    print metadata_filters
    results = generic_find( find_annotations, metadata_filters)
    print "Results:", results
    return results

@route('/find_utterances',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def find_utterances_handler():
    metadata_filters = json.load(request.body)
    print metadata_filters
    results = generic_find( find_utterances, metadata_filters)
    print "Results:", results
    return results

@route('/find_audio_events',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def find_audio_events_handler():
    metadata_filters = json.load(request.body)
    print metadata_filters
    results = generic_find( find_audio_events, metadata_filters)
    print "Results:", results
    return results

@route('/find_pseudoterms',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def find_pseudoterms_handler():
    metadata_filters = json.load(request.body)
    print metadata_filters
    results = generic_find( find_pseudoterms, metadata_filters)
    print "Results*:", results
    return results


@route('/update_pseudoterm',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def update_pseudoterm_header():
    update = json.load(request.body)
    _id = update['_id']
    del update['_id']

    dataset_name = update['dataset']
    del update['dataset']

    db = init_dbconn(name=settings[dataset_name]['DB_NAME'], host=settings[dataset_name]['DB_HOST'])
    res = update_pseudoterm(db, _id, **update)

    return res


@route('/junk_pseudoterm',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def junk_pseudoterm():
    update = json.load(request.body)
    _id = update['_id']
    dataset_name = update['dataset']

    db = init_dbconn(name=settings[dataset_name]['DB_NAME'], host=settings[dataset_name]['DB_HOST'])
    res = pseudoterm_is_junk(db, _id)

    return res


"""Get Venncloud data for a single list of utterances"""
@route('/cloud_data_from_utterances',method=['OPTIONS','POST'])
@json_wrapper
@enable_cors
def cloud_data_handler():
    request_data = json.load(request.body) # Should have a 'dataset' and an 'utterances' field
    dataset = request_data['dataset']

    utterances = request_data['utterances']

    db = init_dbconn(name=settings[dataset]['DB_NAME'], host=settings[dataset]['DB_HOST'])
    print request_data
    token_vector = make_wc_datastructure( db, utterances )

    print "Token Vector:", token_vector[:3]
    return token_vector


@route('/')
def index_page():
    vaporviz_path = os.path.dirname(os.path.realpath(__file__))
    return template('index', current_corpora=current_corpora)


@route('/corpus/<corpus>/audio/audio_event/<audio_event_id>.wav')
def audio_for_audio_event(corpus,audio_event_id):
    """
    Creates a WAV file from a single audio event
    """
    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])
    audio_event = find_audio_events(db, _id=ObjectId(audio_event_id))[0]

    # Create a temporary directory
    tmp_directory = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_directory, 'combined_clips.wav')

    # The first argument to CSoxStream must be a filename with a '.wav' extension.
    #
    # If the output file does not have a '.wav' extension, pysox will raise
    # an "IOError: No such file" exception.
    outfile = pysox.CSoxStream(
        tmp_filename,
        'w',
        settings[corpus]['SOX_SIGNAL_INFO'])

    START_OFFSET = bytes("%f" % (audio_event['start_offset'] / 100.0))
    DURATION = bytes("%f" % (audio_event['duration'] / 100.0))

    utterance = find_utterances(db, _id=audio_event['utterance_id'])[0]
    input_filename = utterance['hltcoe_audio_path']

    infile = pysox.CSoxStream(input_filename)
    chain = pysox.CEffectsChain(infile, outfile)
    chain.add_effect(pysox.CEffect('trim', [START_OFFSET, DURATION]))
    chain.flow_effects()
    infile.close()

    outfile.close()

    # Read in audio data from temporary file
    wav_data = open(tmp_filename, 'rb').read()

    # Clean up temporary files
    os.remove(tmp_filename)
    os.rmdir(tmp_directory)

    return bytestring_as_file_with_mimetype(wav_data, 'audio/wav')


@route('/corpus/<corpus>/audio/pseudoterm/<pseudoterm_id>_audio_events.json')
@json_wrapper
def audio_events_for_pseudoterm(corpus,pseudoterm_id):
    """
    Returns a JSON object with information about the audio events
    associated with a pseudoterm
    """
    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])
    pseudoterm = find_pseudoterms(db, _id=ObjectId(pseudoterm_id))[0]
    audio_event_cursor = find_audio_events(db, pt_id=pseudoterm['_id'])

    audio_events = [audio_event for audio_event in audio_event_cursor]

    audio_identifier_for_utterance_id = {}
    for audio_event in audio_events:
        if audio_event['utterance_id'] not in audio_identifier_for_utterance_id:
            utterance = find_utterances(db, _id=audio_event['utterance_id'])[0]
            audio_identifier_for_utterance_id[audio_event['utterance_id']] = utterance['audio_identifier']
        audio_event['audio_identifier'] = audio_identifier_for_utterance_id[audio_event['utterance_id']]
        audio_event['utterance_id'] = str(audio_event['utterance_id'])

    return audio_events


@route('/corpus/<corpus>/audio/pseudoterm/<pseudoterm_id>.wav')
def audio_for_pseudoterm(corpus,pseudoterm_id):
    """
    Creates a WAV file from multiple audio samples of a single pseudoterm
    """
    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])
    pseudoterm = find_pseudoterms(db, _id=ObjectId(pseudoterm_id))[0]

    # TODO: Allow number of audio events to be specified as parameter, instead
    #       of hard-coded to 10
    audio_events = find_audio_events(db, pt_id=pseudoterm['_id'], count=10)

    # Create a temporary directory
    tmp_directory = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_directory, 'combined_clips.wav')

    # The first argument to CSoxStream must be a filename with a '.wav' extension.
    #
    # If the output file does not have a '.wav' extension, pysox will raise
    # an "IOError: No such file" exception.
    outfile = pysox.CSoxStream(
        tmp_filename,
        'w',
        settings[corpus]['SOX_SIGNAL_INFO'])

    print "audio_for_pseudoterm('%s'):" % pseudoterm_id
    for audio_event in audio_events:
        START_OFFSET = bytes("%f" % (audio_event['start_offset'] / 100.0))
        DURATION = bytes("%f" % (audio_event['duration'] / 100.0))

        utterance = find_utterances(db, _id=audio_event['utterance_id'])[0]
        input_filename = utterance['hltcoe_audio_path']

        print "  [%s] (%d-%d)" % (utterance['hltcoe_audio_path'], audio_event['start_offset'], audio_event['end_offset'])

        infile = pysox.CSoxStream(input_filename)
        chain = pysox.CEffectsChain(infile, outfile)
        chain.add_effect(pysox.CEffect('trim', [START_OFFSET, DURATION]))
        chain.flow_effects()
        infile.close()

    outfile.close()

    # Read in audio data from temporary file
    wav_data = open(tmp_filename, 'rb').read()

    # Clean up temporary files
    os.remove(tmp_filename)
    os.rmdir(tmp_directory)

    return bytestring_as_file_with_mimetype(wav_data, 'audio/wav')


@route('/corpus/<corpus>/audio/pseudoterm/context/<pseudoterm_id>.wav')
def audio_for_pseudoterm_with_context(corpus, pseudoterm_id):
    """
    Creates a WAV file from multiple audio samples of a single pseudoterm
    """
    # TODO: Get seconds of context from HTTP parameter
    SECONDS_OF_CONTEXT = 0.5

    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])
    pseudoterm = find_pseudoterms(db, _id=ObjectId(pseudoterm_id))[0]
    # TODO: Allow number of audio events to be specified as parameter, instead
    #       of hard-coded to 10
    audio_events = find_audio_events(db, pt_id=pseudoterm['_id'], count=10)

    # Create a temporary directory
    tmp_directory = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_directory, 'combined_clips.wav')

    # The first argument to CSoxStream must be a filename with a '.wav' extension.
    #
    # If the output file does not have a '.wav' extension, pysox will raise
    # an "IOError: No such file" exception.
    outfile = pysox.CSoxStream(
        tmp_filename,
        'w',
        settings[corpus]['SOX_SIGNAL_INFO'])

    for audio_event in audio_events:
        initial_start_offset = audio_event['start_offset'] / 100.0
        initial_duration = audio_event['duration'] / 100.0

        if initial_start_offset < SECONDS_OF_CONTEXT:
            start_offset = 0.0
            prefix_duration = initial_start_offset
        else:
            start_offset = initial_start_offset - SECONDS_OF_CONTEXT
            prefix_duration = SECONDS_OF_CONTEXT

        # TODO: Handle case where audio file is too short for requested context length
        suffix_duration = SECONDS_OF_CONTEXT

        duration = prefix_duration + initial_duration + suffix_duration

        print "INITIAL DURATION: %f" % initial_duration
        print "DURATION: %f" % duration

        utterance = find_utterances(db, _id=audio_event['utterance_id'])[0]
        input_filename = utterance['hltcoe_audio_path']

        start_offset = bytes("%f" % start_offset)
        duration = bytes("%f" % duration)

        infile = pysox.CSoxStream(input_filename)
        chain = pysox.CEffectsChain(infile, outfile)
        chain.add_effect(pysox.CEffect('trim', [start_offset, duration]))
        chain.flow_effects()
        infile.close()

    outfile.close()

    # Read in audio data from temporary file
    wav_data = open(tmp_filename, 'rb').read()

    # Clean up temporary files
    os.remove(tmp_filename)
    os.rmdir(tmp_directory)

    return bytestring_as_file_with_mimetype(wav_data, 'audio/wav')


@route('/corpus/<corpus>/audio/utterance/<utterance_id>.wav')
def audio_for_utterance(corpus, utterance_id):
    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])

    utterance = find_utterances(db, _id=ObjectId(utterance_id))[0]
    utterance_filename = utterance['hltcoe_audio_path']

    return static_file(utterance_filename, root="/", mimetype='audio/wav')


@route('/corpus/<corpus>/wordcloud/')
def corpus_wordcloud(corpus):
    return template('corpus_wordcloud', corpus=corpus)


@route('/corpus/<corpus>/')
@route('/corpus/<corpus>/document/list/')
def document_list(corpus):
    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])
    utterance_cursor = find_utterances(db)
    utterance_audio_identifiers = [utt['audio_identifier'] for utt in utterance_cursor]
    utterance_audio_identifiers.sort()
    return template('document_list', utterance_audio_identifiers=utterance_audio_identifiers)


@route('/corpus/<corpus>/document/view/<audio_identifier>')
def document_view(corpus, audio_identifier):
    db = init_dbconn(name=settings[corpus]['DB_NAME'], host=settings[corpus]['DB_HOST'])
    utterance = find_utterances(db, audio_identifier=audio_identifier)[0]
    audio_events = find_audio_events(db, utterance_id=utterance['_id'])
    return template('document',
                    audio_events=audio_events,
                    corpus=corpus,
                    utterance_id=str(utterance['_id']))



parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", default=12321)
args = parser.parse_args()

"""Now actually start the webserver"""
run(host='0.0.0.0', port=args.port, debug=True)
