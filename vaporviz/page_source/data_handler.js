var cloud_datasets = {};


// function display_annotations(annotations){
//
//     /*$.each(annotations,function(index,datum){
//             console.log("---"+index);
//             console.log(datum);
//         });
//     */
//
//     $('#annotations_landing_zone').html(prettyPrint(annotations));
// }
//
// function display_utterances(utterances){
//     $('#utterances_landing_zone').html(prettyPrint(utterances));
// }
//
// function display_pseudoterms(pseudoterms){
//     $('#pseudoterms_landing_zone').html(prettyPrint(pseudoterms));
// }
//
// function display_audio_events(audio_events){
//     $('#audio_events_landing_zone').html(prettyPrint(audio_events));
// }


// function get_annotation(){
//     //dataset_name = $('#dataset_dropdown').val();
//
//     send = {};
//     send.dataset=corpus_name;
//     send.count = 10; //TODO: pull from some element
//
//
//     $.ajaxSetup({
//         contentType: "application/json; charset=utf-8",
//         dataType: "json"
//     });
//
//     $.ajax({
//         url: "/find_annotations",
//         type: "POST",
//         data: JSON.stringify(send),
//         error: function(xhr, error) {
//             alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
//         },
//         success: function(data) {
//             current_annotations = data;
//             display_annotations(data);
//         }
//     });
// }


// function get_utterances(){
//     //dataset_name = $('#dataset_dropdown').val();
//
//     send = {};
//     send.dataset=corpus_name;
//     send.count = 10; //TODO: pull from some element
//
//     $.ajaxSetup({
//         contentType: "application/json; charset=utf-8",
//         dataType: "json"
//     });
//
//     $.ajax({
//         url: "/find_utterances",
//         type: "POST",
//         data: JSON.stringify(send),
//         error: function(xhr, error) {
//             alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
//         },
//         success: function(data) {
//             current_utterances = data;
//             display_utterances(data);
//         }
//     });
// }


// function get_audio_events(){
//
//     send = {};
//     send.dataset=corpus_name;
//     send.count = 10; //TODO: pull from some element
//
//     $.ajaxSetup({
//         contentType: "application/json; charset=utf-8",
//         dataType: "json"
//     });
//
//     $.ajax({
//         url: "/find_audio_events",
//         type: "POST",
//         data: JSON.stringify(send),
//         error: function(xhr, error) {
//             alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
//         },
//         success: function(data) {
//             current_audio_events = data;
//             display_audio_events(data);
//         }
//     });
// }

function get_cloud_data(corpus, utterance_list){

    var utterance_ids = utterance_list.utterance_ids;
    var dataset_name = utterance_list.dataset_name;

    return $.Deferred( function( defer ) {


    send = {};
    send.dataset = corpus;
    send.utterances = utterance_ids;


    $.ajaxSetup({
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    });

    $.ajax({
        url: "/cloud_data_from_utterances",
        type: "POST",
        data: JSON.stringify(send),
        error: function(xhr, error) {
            alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
            defer.reject('Deferred error message');
        },
        success: function(data) {
            //cloud_datasets = [data];
            wc_data = {};
            wc_data.dataset_name = dataset_name;
            wc_data.tokens = data;
            wc_data.num_tokens = data.length;
            wc_data.num_documents = utterance_ids.length;
            cloud_datasets[dataset_name] = wc_data;
            //$('#cloud_data_landing_zone').html(prettyPrint(data));
            defer.resolve(data);
        }
    });
    }).promise();
}



function get_pseudoterm(pt_id, corpus_name){

    send = {};
    send.dataset=corpus_name;
    send.count = 1;
    send._id=(pt_id);

    $.ajaxSetup({
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    });

    $.ajax({
        url: "/find_pseudoterms",
        type: "POST",
        data: JSON.stringify(send),
        error: function(xhr, error) {
            alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
        },
        success: function(data) {
            active_pseudoterm = data[0]; //Global var
            $('#pt_eng_display')
                .val(active_pseudoterm.eng_display);

            $('#pt_native_display')
                .val(active_pseudoterm.native_display);
            $('#pt_stats_landing_zone')
                .html(prettyPrint(active_pseudoterm));
            $('#pt_snippets_play_button')
                .click(function(){playPseudoterm('pt_player', pt_id);});
            $('#pt_snippets_play_button')
                .click(function(){playPseudoterm_with_context('pt_player', pt_id);});

            //Also get audioevents and snippets
        }
    });
}

// function get_pseudoterms(count){
//
//     send = {};
//     send.dataset=corpus_name;
//     send.count = count || 10; //TODO: pull from some element
//
//     $.ajaxSetup({
//         contentType: "application/json; charset=utf-8",
//         dataType: "json"
//     });
//
//     $.ajax({
//         url: "/find_pseudoterms",
//         type: "POST",
//         data: JSON.stringify(send),
//         error: function(xhr, error) {
//             alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
//         },
//         success: function(data) {
//             current_pseudoterms = data;
//             //display_pseudoterms(data);
//             active_pseudoterm = data[0]; //Global var
//         }
//     });
// }

// function get_audio_events_from_pseudoterm(pseudoterm_id, count){
//
//     send = {};
//     send.dataset=corpus_name;
//     send.pt_id=pseudoterm_id;
//     send.count= count || 10; //10 if nothing is specified in the call
//     $.ajax({
//         url: "/find_audio_events",
//         type: "POST",
//         data: JSON.stringify(send),
//         error: function(xhr, error) {
//             alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
//         },
//         success: function(data) {
//             display_audio_events(data);
//         }
//     });
// }

function annotate_pt_eng_label(corpus){
    active_pt_id = active_pseudoterm._id;
    annotation = $('#pt_eng_display').val();
    if (active_pseudoterm.eng_display == annotation){
        return;
    }
    else {
        send = {};
        send.dataset=corpus;
        send._id=active_pt_id;
        send.eng_display = annotation;
        send.annotated = true;
        $.ajax({
            url: "/update_pseudoterm",
            type: "POST",
            data: JSON.stringify(send),
            error: function(xhr, error) {
                alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
            },
            success: function(data) {
                get_pseudoterm(active_pt_id, corpus);
            }
        });
        //TODO: Issue a call to redraw that token of the wordcloud.
        //alert('updating'+send.eng_display);
        update_displayed_token( active_pseudoterm.eng_display , annotation);
    }
}


function annotate_pt_native_label(corpus){
    active_pt_id = active_pseudoterm._id;
    annotation = $('#pt_native_display').val();
    send = {};
    send.dataset=corpus;
    send._id=active_pt_id;
    send.native_display = annotation;
    $.ajax({
        url: "/update_pseudoterm",
        type: "POST",
        data: JSON.stringify(send),
        error: function(xhr, error) {
            alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
        },
        success: function(data) {
            //Reload the PT now to see the changes reflected
            get_pseudoterm(active_pt_id, corpus);
        }
    });
}

function junk_this_pseudoterm(){
    active_pt_id = active_pseudoterm._id;
    send = {};
    send.dataset = corpus_name;
    send._id=active_pt_id;
    send.native_display = annotation;
    $.ajax({
        url: "/junk_pseudoterm",
        type: "POST",
        data: JSON.stringify(send),
        error: function(xhr, error) {
            alert('Error!  Status = ' + xhr.status + ' Message = ' + error);
        },
        success: function(data) {
            //Reload the PT now to see the changes reflected
            //get_pseudoterm( active_pt_id );
        }
    });

    junk_displayed_token( active_pseudoterm.eng_display );
}


// function test_ajax_calls(){
//     get_annotation();
//     get_utterances();
//     get_audio_events();
//     get_pseudoterms();
// }

// function test_cloud_data_call(){
//     utterances = ['53627c6e04dc077fb2110b78','53627c6e04dc077fb211149b','53627c6f04dc077fb21122e7'];
//     $.when(get_cloud_data(utterances)).done( function(data){
//         $('#cloud_data_landing_zone').html(prettyPrint(data));
//     });
// }

// //Deprecated, to be looked at again later
// function get_multiple_utterances_cloud_data( utterances_lists ){
//     get_cloud_data(utterances);
//     return $.Deferred( function(defer) {
//         $.each( utterance_list, function(index, utt_list) {
//             dataset_name = utt_list.dataset_name;
//             get_cloud_data( utt_list.utterance_ids, utt_list.dataset_name);
//         });
//         defer.resolve();
//     }).promise();
// }


/*
  set_up_annotate_pseudoterm_id() is a callback handler that is
  invoked when a user clicks on a word in a wordcloud.

  The callback function is assigned from make_me_a_venncloud() in
  Glen's dynamic_wordclouds.js.  The make_me_a_venncloud() function
  does not allow any parameters but 'token' to be passed to callback
  functions for words in the wordcloud - but we need to pass a 'corpus'
  parameter to set_up_annotate_pseudoterm_id().

  We use a constructor function to create a closure that allows
  set_up_annotate_pseudoterm_id() to access the 'corpus' parameter,
  without storing the 'corpus' parameter in a global variable.
*/
var CorpusClosureForSetupAnnotatePseudotermID = function(corpus) {
  this.corpus = corpus;
  this.set_up_annotate_pseudoterm_id = function(token) {
      if (token.length > 50){ return; } //If you mistakenly click the whole box
      $.get('/www/pseudoterm_template.html',function(data){
          alert("in");
          $('#annotation_landing_zone').html(data);
          alert("Past");
      });

      var token_container = master_datasets[selected_datasets[0]].tokens[token] ||
          master_datasets[selected_datasets[1]].tokens[token] ||
          [];
      var pt_ids = token_container.pt_ids;
      console.log(pt_ids);
      pseudotermID = pt_ids[0]['$oid'];
      get_pseudoterm(pseudotermID, corpus); //Also posts to the global variable

      var visualizerID = "waveform_visualizer";  // HARDCODE
      waveformVisualizerLoadAndPlayURL(visualizerID, getURLforPseudotermWAV(corpus, pseudotermID));

      $("#pt_eng_display")
          .focusout(function(){
              annotate_pt_eng_label(corpus);
          });

      $("#pt_native_display")
          .focusout(function(){
              annotate_pt_native_label(corpus);
          });

      //Autoselect the english display element
      $('#pt_eng_display').focus().select();
  };
};


function venncloud_from_utterances(corpus, utterances_lists){
    var corpus_closure = new CorpusClosureForSetupAnnotatePseudotermID(corpus);

    options = {};
    options.click = corpus_closure.set_up_annotate_pseudoterm_id;

    //options.wordcloud_element = 'cloud_data_landing_zone';

    //$.when(get_multiple_utterances_cloud_data(utterances_lists)).done( function(){
    //HARDCODED below for the nonce.
    u = utterances_lists;
    $.when(get_cloud_data(corpus, u[0] ), get_cloud_data(corpus, u[1] )).done( function(){
        //user cloud datasets
        make_me_a_venncloud( cloud_datasets, options );
    });
}
