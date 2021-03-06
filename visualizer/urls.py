from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^corpus_wordcloud_params', views.wordcloud_params_for_corpus, name='wordcloud_params_for_corpus'),
    url(r'^document_wordcloud_params', views.wordcloud_params_for_document, name='wordcloud_params_for_document'),
    url(r'^document_topic_wordcloud_params/(?P<document_topic_id>\d+)', views.wordcloud_params_for_document_topic,
        name='wordcloud_params_for_document_topic'),

    url(r'^\d+/terms.json/(?P<term_id>\d+)', views.term_update, name='term_update_corpus_termcloud'),
    url(r'^(?P<corpus_id>\d+)/terms.json', views.wordcloud_json_for_corpus, name='wordcloud_json_for_corpus'),
    url(r'^(?P<corpus_id>\d+)/lorelei_situation_frames.json', views.lorelei_situation_frames_json,
        name='lorelei_situation_frames_json'),
    url(r'^(?P<corpus_id>\d+)/document/(?P<document_id>\d+)/audio_fragments.json',
        views.document_audio_fragments_as_json, name='document_audio_fragments_as_json'),

    url(r'^\d+/document/\d+/terms.json/(?P<term_id>\d+)', views.term_update, name='term_update_document_termcloud'),
    url(r'^(?P<corpus_id>\d+)/document/(?P<document_id>\d+)/terms.json',
        views.wordcloud_json_for_document, name='wordcloud_json_for_document'),
    url(r'^(?P<corpus_id>\d+)/document/(?P<document_id>\d+)/topics.json',
        views.document_topic_json_for_document, name='document_topic_json_for_document'),
    url(r'^(?P<corpus_id>\d+)/document/(?P<document_id>\d+)/document_topic/update',
        views.document_topic_for_document_update, name='document_topic_for_document_update'),
    url(r'^(?P<corpus_id>\d+)/document/(?P<document_id>\d+)/', views.document, name='document'),
    url(r'^(?P<corpus_id>\d+)/document/list/', views.corpus_document_list, name='corpus_document_list'),
    url(r'^(?P<corpus_id>\d+)/document/(?P<document_id>\d+).wav', views.document_wav_file, name='document_wav_file'),

    url(r'^(?P<corpus_id>\d+)/document_topic/(?P<document_topic_id>\d+)/terms.json',
        views.wordcloud_json_for_document_topic, name='wordcloud_json_for_document_topic'),
    url(r'^(?P<corpus_id>\d+)/document_topic/(?P<document_topic_id>\d+)/', views.document_topic, name='document_topic'),

    url(r'^term/(?P<term_id>\d+)/update', views.term_update, name='term_update'),
    url(r'^(?P<corpus_id>\d+)/term/(?P<term_id>\d+).wav', views.term_wav_file, name='term_wav_file'),
    url(r'^(?P<corpus_id>\d+)/term/(?P<term_id>\d+)_audio_fragments.json',
        views.term_audio_fragments_as_json, name='term_audio_fragments_as_json'),

    url(r'^(?P<corpus_id>\d+)/wordcloud/', views.corpus_wordcloud, name='corpus_wordcloud'),
]
