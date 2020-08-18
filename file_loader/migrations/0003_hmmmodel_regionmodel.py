# Generated by Django 3.1 on 2020-08-17 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('file_loader', '0002_auto_20200817_1441'),
    ]

    operations = [
        migrations.CreateModel(
            name='HMMModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('extension', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'hmm_model',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegionModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('extension', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'region_model',
                'abstract': False,
            },
        ),
    ]
