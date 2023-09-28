# Generated by Django 3.1.14 on 2023-09-15 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_auto_20230530_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapbaselayer',
            name='portal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='map_base_layers', to='portal.portal', verbose_name='Portal'),
        ),
        migrations.AlterField(
            model_name='maplayer',
            name='portal',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='layers', to='portal.portal', verbose_name='Portal'),
        ),
    ]
