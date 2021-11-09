# Generated by Django 3.1.13 on 2021-11-09 10:20

from django.db import migrations
from django.contrib.gis.geos import Point


def add_source_location_every_stream(apps, schema_editor):
    StreamModel = apps.get_model('river', 'Stream')
    for stream in StreamModel.objects.all():
        if not stream.source_location:
            stream.source_location = Point(stream.geom[0])
            stream.save()


def remove_source_location_every_stream(apps, schema_editor):
    StreamModel = apps.get_model('river', 'Stream')
    for stream in StreamModel.objects.all():
        if stream.source_location:
            stream.source_location = None
            stream.save()


class Migration(migrations.Migration):

    dependencies = [
        ('river', '0011_stream_source_location'),
    ]

    operations = [
        migrations.RunPython(add_source_location_every_stream, remove_source_location_every_stream)
    ]
