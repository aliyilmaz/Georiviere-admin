# Generated by Django 3.1.14 on 2023-07-24 15:02

from django.db import migrations, models
import django.db.models.deletion
import georiviere.contribution.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contribution', '0003_auto_20230601_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContributionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_insert', models.DateTimeField(auto_now_add=True, verbose_name='Insertion date')),
                ('date_update', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Update date')),
                ('label', models.CharField(max_length=128, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Status',
            },
        ),
        migrations.CreateModel(
            name='SelectableUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='contribution',
            name='assigned_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contributions', to='contribution.selectableuser', verbose_name='Supervisor'),
        ),
        migrations.AddField(
            model_name='contribution',
            name='status_contribution',
            field=models.ForeignKey(blank=True, default=georiviere.contribution.models.status_default, null=True, on_delete=django.db.models.deletion.PROTECT, to='contribution.contributionstatus', verbose_name='Status'),
        ),
    ]
