# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompileDailyServerUsage',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('normal_usage_server_count', models.IntegerField()),
                ('low_usage_server_count', models.IntegerField()),
                ('nearly_no_usage_server_count', models.IntegerField()),
                ('high_usage_server_count', models.IntegerField()),
                ('region', models.CharField(max_length=3)),
            ],
            options={
                'db_table': 'compile_daily_server_usage',
            },
        ),
        migrations.CreateModel(
            name='CompileServerUsageInfo',
            fields=[
                ('date', models.DateField(null=True, blank=True)),
                ('hostname', models.CharField(max_length=255, null=True, blank=True)),
                ('owner', models.CharField(max_length=255, null=True, blank=True)),
                ('ipaddress', models.CharField(max_length=255, null=True, blank=True)),
                ('cpu_load_gt_50_coun', models.IntegerField(null=True, blank=True)),
                ('total_memory', models.CharField(max_length=255, null=True, blank=True)),
                ('total_cpu_cores', models.IntegerField(null=True, db_column='total_CPU_cores', blank=True)),
                ('largest_disk_mount_point', models.CharField(max_length=255, null=True, blank=True)),
                ('total_diskspace', models.CharField(max_length=255, null=True, blank=True)),
                ('used_diskspace', models.CharField(max_length=255, null=True, blank=True)),
                ('disk_used_ratio', models.FloatField(null=True, blank=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'compile_server_usage_info',
            },
        ),
        migrations.CreateModel(
            name='ScmDailyServerUsage',
            fields=[
                ('id', models.IntegerField()),
                ('date', models.DateField(serialize=False, primary_key=True)),
                ('servertotalcount', models.IntegerField(null=True, db_column='ServerTotalCount', blank=True)),
                ('assignedservercount', models.IntegerField(db_column='AssignedServerCount')),
                ('servernotinusecount', models.IntegerField(null=True, db_column='ServerNotInUSeCount', blank=True)),
                ('usedratio', models.FloatField(null=True, db_column='UsedRatio', blank=True)),
            ],
            options={
                'db_table': 'scm_daily_server_usage',
            },
        ),
        migrations.CreateModel(
            name='ScmDailyServerUsageSeparate',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('servertotalcount', models.IntegerField(null=True, db_column='ServerTotalCount', blank=True)),
                ('region', models.CharField(unique=True, max_length=4)),
                ('assignedservercount', models.IntegerField(db_column='AssignedServerCount')),
                ('servernotinusecount', models.IntegerField(null=True, db_column='ServerNotInUSeCount', blank=True)),
                ('usedratio', models.FloatField(null=True, db_column='UsedRatio', blank=True)),
            ],
            options={
                'db_table': 'scm_daily_server_usage_separate',
            },
        ),
        migrations.CreateModel(
            name='ScmDailyServerWsUsageSeparate',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('servertotalcount', models.IntegerField(null=True, db_column='ServerTotalCount', blank=True)),
                ('region', models.CharField(unique=True, max_length=4)),
                ('assignedservercount', models.IntegerField(db_column='AssignedServerCount')),
                ('servernotinusecount', models.IntegerField(null=True, db_column='ServerNotInUSeCount', blank=True)),
                ('usedratio', models.FloatField(null=True, db_column='UsedRatio', blank=True)),
            ],
            options={
                'db_table': 'scm_daily_server_ws_usage_separate',
            },
        ),
        migrations.CreateModel(
            name='VmSummary',
            fields=[
                ('date', models.DateField(db_column='Date')),
                ('region', models.CharField(max_length=255, null=True, db_column='Region', blank=True)),
                ('vm_type', models.CharField(max_length=255, null=True, db_column='VM_type', blank=True)),
                ('total', models.IntegerField()),
                ('assigned', models.IntegerField(db_column='Assigned')),
                ('noassigned', models.IntegerField(db_column='NoAssigned')),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'vm_summary',
            },
        ),
    ]
