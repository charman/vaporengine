<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/www/jquery-ui.css">
  <link rel="stylesheet" href="/www/dynamic_wordclouds.css">

  <link rel="stylesheet" href="/static/bootstrap-3.1.1/css/bootstrap.css"/>
  <link rel="stylesheet" href="/static/bootstrap-3.1.1/css/bootstrap-theme.css"/>

  <script src="/static/jquery-1.11.0.min.js"></script>
  <script src="/static/bootstrap-3.1.1/js/bootstrap.js"></script>

  <script src="/www/jquery-ui.js"></script>
  <script src="/www/floating-1.12.js"></script>
  <script src="/www/dynamic_wordclouds.js"></script>
  <script src="/www/prettyprint.js"></script>

  <script src="/static/wavesurfer/wavesurfer.js"></script>
  <script src="/static/wavesurfer/webaudio.js"></script>
  <script src="/static/wavesurfer/webaudio.buffer.js"></script>
  <script src="/static/wavesurfer/webaudio.media.js"></script>
  <script src="/static/wavesurfer/drawer.js"></script>
  <script src="/static/wavesurfer/drawer.canvas.js"></script>

  <script src="/www/vapor_audio.js"></script>
  <script src="/www/data_handler.js"></script>

  <style>
    /* Hide drop-down boxes for selecting Left and Right datasets */
    #wordcloud_landing_zone thead {
      display: none;
    }
  </style>

  <script>
    function create_wordcloud_for_utterance(utterance_id) {
      var utterance_set1 = {
        'dataset_name': 'Set1',
        'utterance_ids': [utterance_id]
      };

      venncloud_from_utterances([utterance_set1, utterance_set1]);
    }

    $(document).ready(function() {
      create_wordcloud_for_utterance("{{utterance_id}}");

      addWaveformVisualizer('waveform_visualizer');
      addControlsForWaveformVisualizer($('#pt_snippets_audio_player'), 'waveform_visualizer');
    });

    $.get("/www/venncloud_template.html", function(data){
      $('#cloud_data_landing_zone').html(data);
    });
  </script>
</head>
<body style="padding-top: 250px;">

<div class="container">
  <nav class="navbar navbar-default navbar-fixed-top" role="navigation">
    <div class="container-fluid">
      <div style="border: 1px solid #C0C0C0; margin-top: 0.5em; margin-bottom: 0.5em;">
        <div id="waveform_visualizer"></div>
      </div>
      <div>
        <div class="form-inline">
          <div class="form-group">
            <span id="pt_snippets_audio_player"></span>
          </div>
          <div class="form-group">
            <label for="pt_eng_display">English</label>
            <input id="pt_eng_display"></input>
          </div>
          <div class="form-group">
            <label for="pt_native_display">Native</label>
            <input id="pt_native_display" disabled></input>
          </div>
          <div class="form-group">
            <div id="waveform_visualizer_utterance_list" style="padding-left: 1em;"></div>
          </div>
        </div>
      </div>
      <!-- Commented out code below: Experiments replacing existing wordcloud menus
           with Bootstrap-styled wordcloud menus
      -->
      <div style="margin: 0.5em;">
        <div class="btn-group">
          <!--
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              Entities
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu" role="menu">
              <li><a href="#">Action</a></li>
            </ul>
          </div>
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              Common Cloud
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu" role="menu">
              <li><a href="#">Action</a></li>
            </ul>
          </div>
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              TF filter
              <span class="caret"></span>
            </button>
          </div>
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              IDF filter
              <span class="caret"></span>
            </button>
          </div>
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              Size
              <span class="caret"></span>
            </button>
          </div>
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              Opacity
              <span class="caret"></span>
            </button>
          </div>
          -->
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              Sort by
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu" role="menu" style="padding-left: 1em;" id="radio">
              <li>
                <input type="radio" id="ALPHABETIC" name="radio" checked="checked" />
                <label for="ALPHABETIC">Alphabetic</label>
              </li>
              <li>
                <input type="radio" id="COUNT" name="radio" />
                <label for="COUNT">Frequency of Occurence</label>
              </li>
              <li>
                <input type="radio" id="IDF" name="radio" />
                <label for="IDF">Rarity in Corpus</label>
              </li>
            </ul>
          </div>
          <!--
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
              Legend
              <span class="caret"></span>
            </button>
          </div>
          -->
        </div>
      </div>
    </div>
  </nav>

  <!-- Hiding Glen's controls until they can be converted to use Bootstrap
       styling.  Controls are set to 'display: none;' instead of being
       commented out or deleted because the VennCloud JavaScript code
       will break if some of the DOM elements in the controls don't exist.
  -->
  <div style="display: none;">
    <table width="600px">
      <tr>
        <td valign="top" width="100%">
          <table border=1 cellspacing=0 cellpadding=3 width="100%">
            <tr>
              <td align="center" onclick="hide_all_controls()" class="button">
                <b>[X]</b>
              </td>
              <td id="wordcloud_entities_button" class="button"
                  width="75px" onclick="toggle_wordcloud_entities_buttons()"
                  align="center">
                entities
              </td>
              <td id="common_cloud_control_button"
                  width="75px" onclick="toggle_wordcloud_common_cloud_controls()"
                  align="center" class="button">
                common cloud
              </td>
              <td id="frequency_filter_button"
                  width="75px" onclick="toggle_wordcloud_frequency_filter()"
                  align="center" class="button">
                tf filter
              </td>
              <td id="rarity_filter_button"
                  width="75px" onclick="toggle_wordcloud_rarity_filter()"
                  align="center" class="button">
                idf filter
              </td>
              <td id="size_control_button"
                  width="75px" onclick="toggle_wordcloud_size_controls()"
                  align="center" class="button">
                size controls
              </td>
              <td id="opacity_control_button"
                  width="75px" onclick="toggle_wordcloud_opacity_controls()"
                  align="center" class="button">
                opacity controls
              </td>
              <td id="wordcloud_sort_by_button"
                  width="75px" onclick="toggle_wordcloud_sort_buttons()"
                  align="center" class="button">
                sort by
              </td>
              <td id="wordcloud_description_button"
                  width="75px" onclick="toggle_wordcloud_description()"
                  align="center" class="button">
                legend
              </td>
              <td align="center" class="button">
                do not redraw <input type="checkbox" onclick="toggle_do_not_redraw_wordcloud()">
              </td>
              <td align="center" class="button">
                highlight keywords <input type="checkbox" onclick="toggle_highlight_keywords_wordcloud()">
              </td>
            </tr>
          </table>

          <div id="wordcloud_common_cloud_controls"
               style="z-index:1; position:absolute; background-color:#ffffff; padding 5 spacing 5" class="menu">
            <table width="300px" style="background-color:White;" id="menu_table">
              <tr style="background-color:#ffffff;">
                <td id="menu_td">
                  -
                </td>
                <td id="menu_td" width="90%">
                  <div id='common_cloud_controls'></div>
                </td>
                <td id="menu_td">
                  +
                </td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_frequency_filter_controls"
               style="z-index:1; position:absolute; background-color:#ffffff; padding:5; spacing:5" class="menu">
            <table width="300px" style="background-color:White;" id="menu_table">
              <tr style="background-color:#ffffff;">
                <td id="menu_td">
                  <div id='required_observations_slider'></div>
                </td>
              </tr>
              <tr>
                <td id="menu_td">
                  Required Times Observed:<span id="required_observations_out"></span>
                </td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_rarity_filter_controls"
               style="z-index:1; position:absolute; background-color:#ffffff; padding 5 spacing 5" class="menu">
            <table width="300px" style="background-color:White;" id="menu_table">
              <tr style="background-color:#ffffff;">
                <td id="menu_td">
                  <div id='required_idf_slider'></div>
                </td>
              </tr>
              <tr>
                <td id="menu_td">
                  Occurs between <span id="required_idf_out">x</span> documents.
                </td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_size_controls"
               style="z-index:1; position:absolute; background-color:#ffffff; padding 5 spacing 5" class="menu">
            <table width="400px" style="background-color:White;" id="menu_table">
              <tr style="background-color:#ffffff;">
                <td width="20%" align="left" id="menu_td"><b>Frequency: 0</b></td>
                <td width="75%" id="menu_td">
                  <div id="size_frequency_slider"></div>
                </td>
                <td rowspan="2" width="10%" id="menu_td" align="center"><b>+</b></td>
              </tr>
              <tr>
                <td width="20%" align="left" id="menu_td"><b>Rarity: 0</b></td>
                <td id="menu_td">
                  <div id="size_rarity_slider"></div>
                </td>
              </tr>
              <tr>
                <td id="menu_td">Smaller</td>
                <td id="menu_td">
                  <div id="base_fontsize_slider"></div>
                </td>
                <td id="menu_td">Larger</td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_opacity_controls"
               style="z-index:1; position:absolute; background-color:#ffffff; padding 5 spacing 5" class="menu">
            <table width="400px" style="background-color:White;" id="menu_table">
              <tr style="background-color:#ffffff;">
                <td width="20%" align="left" id="menu_td"><b>Frequency: <span align=right>0</span></b></td>
                <td width="80%" id="menu_td">
                  <div id="opacity_frequency_slider"></div>
                </td>
                <td rowspan="2" width="10%" id="menu_td" align="center"><b>+</b></td>
              </tr>
              <tr>
                <td width="20%" align="left" id="menu_td"><b>Rarity: <span align=right>0</span></b></td>
                <td id="menu_td">
                  <div id="opacity_rarity_slider"></div>
                </td>
              </tr>
              <tr>
                <td id="menu_td">Light</td>
                <td id="menu_td">
                  <div id="base_opacity_slider"></div>
                </td>
                <td id="menu_td">Dark</td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_sort_buttons"
               style="z-index:1; position:absolute; background-color:#ffffff; padding:5; spacing:5;" class="menu">
            <table id="menu_table">
              <tr>
                <td id="menu_td">
                  <div id="radio">
                    <input type="radio" id="ALPHABETIC" name="radio" checked="checked"><label
                      for="ALPHABETIC">Alphabetic</label>
                    <input type="radio" id="COUNT" name="radio"><label for="COUNT">Frequency of
                      Occurence</label>
                    <input type="radio" id="IDF" name="radio"><label for="IDF">Rarity in Corpus</label>
                  </div>
                </td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_entities_buttons"
               style="z-index:1; position:absolute; background-color:#ffffff; padding:5; spacing:5;" class="menu">
            <table id="menu_table">
              <tr>
                <td id="menu_td">
                  <div id="entities_buttons">
                    <input type="checkbox" id="display_plain_words" name="display_plain_words"
                           checked="checked"><label for="display_plain_words">Words</label></input>
                    <input type="checkbox" id="display_user_mentions" name="display_user_mentions"
                           checked="checked"><label for="display_user_mentions">@Usernames</label></input>
                    <input type="checkbox" id="display_hashtags" name="display_hashtags"
                           checked="checked"><label for="display_hashtags">#Hashtags</label></input>
                  </div>
                </td>
              </tr>
            </table>
          </div>

          <div id="wordcloud_description_output"
               style="z-index: 1; position:absolute; background:#ffffff; padding:5; spacing:5" class="menu">
            Description of how wordcloud was computed goes here
          </div>
        </td>
      </tr>
    </table>
  </div><!-- /style="display: none:" -->

  <div id="wordcloud_landing_zone"></div>

</div><!-- /.container -->

</body>
</html>
