# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-20 16:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AudioFragment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zr_fragment_index', models.IntegerField(db_index=True)),
                ('start_offset', models.IntegerField()),
                ('end_offset', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('score', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Corpus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('audio_rate', models.IntegerField()),
                ('audio_channels', models.IntegerField()),
                ('audio_precision', models.IntegerField()),
                ('protected_corpus', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_index', models.IntegerField()),
                ('audio_path', models.TextField()),
                ('audio_identifier', models.TextField()),
                ('duration', models.IntegerField()),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Corpus')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField()),
                ('description', models.TextField(default='')),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Corpus')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTopicTermInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(db_index=True, max_length=20)),
                ('score', models.FloatField()),
                ('document_topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.DocumentTopic')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTranscript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Document')),
            ],
        ),
        migrations.CreateModel(
            name='SituationFrameLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Document')),
                ('documenttopic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.DocumentTopic')),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField()),
                ('zr_term_index', models.IntegerField(db_index=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Corpus')),
            ],
        ),
        migrations.CreateModel(
            name='TermCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Corpus')),
                ('terms', models.ManyToManyField(to='visualizer.Term')),
            ],
        ),
        migrations.AddField(
            model_name='documenttopicterminfo',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Term'),
        ),
        migrations.AddField(
            model_name='documenttopic',
            name='documents',
            field=models.ManyToManyField(through='visualizer.SituationFrameLabel', to='visualizer.Document'),
        ),
        migrations.AddField(
            model_name='audiofragment',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Document'),
        ),
        migrations.AddField(
            model_name='audiofragment',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualizer.Term'),
        ),
    ]
