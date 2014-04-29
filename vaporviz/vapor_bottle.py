# Python standard library modules
import argparse
import datetime as dt
import os
import tempfile

# Third party modules
from bottle import route, run, request, response, static_file
import bson.json_util
import pysox
try:
    import ujson as json
except:
    import json

# Local modules
from lib.database import init_dbconn
from vaporgasp.queries import (find_annotations, find_utterances,
                               find_pseudoterms, find_audio_events)
    
# the decorator to ease some javascript pain (if memory serves)
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

def json_wrapper(method):
    def rapper(*a, **kw):
        resp = method(*a, **kw)
        response.content_type = 'application/json'

        # bson.json_util.dumps() knows how to convert Mongo ObjectId's to JSON
        return bson.json_util.dumps(resp)
    return rapper


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


def generic_find(find_function, metadata_filters):
    """Does all the requisite conversions for pulling from the database
    and preparing to serve to the website.
    `find_function` should be one of the function from queries.py"""
    print metadata_filters
    dataset = metadata_filters['dataset'] #This maps to MongoDB table name
    print "from dataset:", dataset
    del metadata_filters['dataset']

    #SECURITY add whitelist of dataset names permitted
    db = init_dbconn(name = dataset, host='r4n7')

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
    print "Results:", results
    return results


@route('/gujarati/<filepath:path>')
def audio_static(filepath):
    # TODO: Retrieve audio file paths from Mongo, instead of hard-coding
    return static_file(filepath, root='/home/hltcoe/ajansen/QASW/audio', mimetype='audio/wav')


@route('/BUCKEYE/<filepath:path>')
def audio_static(filepath):
    # TODO: Retrieve audio file paths from Mongo, instead of hard-coding
    return static_file(filepath, root='/home/hltcoe/ajansen/aren_local/BUCKEYE', mimetype='audio/wav')

@route('/pt_combine_test')
def pt_combine_test():
    """
    Creates a WAV file from multiple audio samples of a single pseudoterm
    """
    db = init_dbconn(name='buckeye', host='localhost')
    first_pseudoterm = find_pseudoterms(db)[0]
    audio_events = find_audio_events(db, pt_id=first_pseudoterm['_id'])

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
        pysox.CSignalInfo(8000.0,1,14))  # TODO: Don't hard-code sample rate

    # TODO: Allow number of audio events to be specified as parameter, instead
    #       of hard-coded to 10
    for audio_event in audio_events[:10]:
        START_OFFSET = bytes("%f" % (audio_event['start_offset'] / 100.0))
        DURATION = bytes("%f" % (audio_event['duration'] / 100.0))

        utterance = find_utterances(db, _id=audio_event['utterance_id'])[0]
        input_filename = utterance['hltcoe_audio_path']

#        print "START: %f, DURATION: %f, filename: %s" % (
#            audio_event['start_offset'] / 100.0,
#            audio_event['duration'] / 100.0,
#            input_filename)

        infile = pysox.CSoxStream(input_filename)
        chain = pysox.CEffectsChain(infile, outfile)
        chain.add_effect(pysox.CEffect('trim', [START_OFFSET, DURATION]))
        chain.flow_effects()
        infile.close()

    outfile.close()

    # Read in audio data from temporary file
#    wav_data = open(tmp_filename, 'rb').read()

    # Clean up temporary files
#    os.remove(tmp_filename)
#    os.rmdir(tmp_directory)

#    return wav_data

    # TODO: How do we return a bytestring with a specific mimetype using Bottle?
    #       Bottle's static_file() allows us to specify a mime-type for an
    #       existing file, but we want to return a byte-array that was created
    #       in memory.
    return static_file(tmp_filename, root="/", mimetype='audio/wav')


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", default=12321)
args = parser.parse_args()

"""Now actually start the webserver"""
run(host='0.0.0.0', port=args.port, debug=True)
