# Generated by Django 2.2.11 on 2023-06-13 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    replaces = [
        ("users", "0002_auto_20200319_0634"),
        ("users", "0003_user_verified"),
        ("users", "0004_auto_20200321_0556"),
        ("users", "0005_auto_20200321_0601"),
        ("users", "0006_user_deleted"),
        ("users", "0007_auto_20200321_2029"),
        ("users", "0008_auto_20200321_2035"),
        ("users", "0009_auto_20200325_1908"),
        ("users", "0010_populate_district"),
        ("users", "0011_map_users_to_district"),
        ("users", "0012_auto_20200326_0342"),
        ("users", "0013_auto_20200327_0437"),
        ("users", "0014_restart_sequence_districts"),
        ("users", "0012_auto_20200326_1752"),
        ("users", "0013_auto_20200326_2021"),
        ("users", "0015_merge_20200327_1215"),
        ("users", "0016_auto_20200327_1954"),
        ("users", "0017_auto_20200328_2256"),
        ("users", "0018_auto_20200328_1853"),
        ("users", "0019_auto_20200328_2226"),
        ("users", "0020_auto_20200401_0930"),
        ("users", "0021_make_kerala_everyones_state"),
        ("users", "0022_auto_verify_users_with_facility"),
        ("users", "0023_auto_20200413_1301"),
        ("users", "0024_auto_20200801_1844"),
        ("users", "0025_auto_20200914_2027"),
        ("users", "0026_auto_20200914_2034"),
        ("users", "0027_auto_20200914_2052"),
        ("users", "0028_auto_20200916_0008"),
        ("users", "0029_ward"),
        ("users", "0030_auto_20200921_1659"),
        ("users", "0031_auto_20200927_1325"),
        ("users", "0032_user_ward"),
        ("users", "0033_auto_20201011_1908"),
        ("users", "0034_auto_20201122_2013"),
        ("users", "0035_auto_20210511_2105"),
        ("users", "0036_auto_20210515_2048"),
        ("users", "0037_auto_20210519_1826"),
        ("users", "0038_user_alt_phone_number"),
        ("users", "0039_auto_20210616_1634"),
        ("users", "0040_auto_20210616_1821"),
        ("users", "0041_user_asset"),
        ("users", "0042_user_created_by"),
        ("users", "0043_auto_20220624_1119"),
        ("users", "0044_user_home_facility"),
        ("users", "0045_auto_20230110_1120"),
        ("users", "0046_auto_20230204_1733"),
        ("users", "0047_user_external_id"),
        ("users", "0048_auto_20230609_1411"),
        ("users", "0049_auto_20230609_1413"),
    ]

    dependencies = [
        ("facility", "0001_initial_squashed"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="asset",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="facility.Asset",
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="home_facility",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="facility.Facility",
            ),
        ),
    ]
