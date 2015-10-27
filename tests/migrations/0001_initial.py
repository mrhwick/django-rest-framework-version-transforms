# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OtherTestModel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('test_field_one', models.CharField(max_length=20)),
                ('test_field_two', models.CharField(max_length=20)),
                ('test_field_three', models.CharField(max_length=20)),
                ('test_field_four', models.CharField(max_length=20)),
                ('test_field_five', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TestModelV3',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('test_field_two', models.CharField(max_length=20)),
                ('test_field_three', models.CharField(max_length=20)),
                ('test_field_four', models.CharField(max_length=20)),
                ('test_field_five', models.CharField(max_length=20)),
                ('new_test_field', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='othertestmodel',
            name='some_foreign_key',
            field=models.ForeignKey(related_name='new_related_object_id_list', to='tests.TestModelV3'),
        ),
    ]
