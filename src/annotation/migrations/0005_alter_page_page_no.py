# Generated by Django 5.0 on 2024-04-02 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0004_entry_entrypages_remove_page_ux_volume_id_page_no_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='page_no',
            field=models.PositiveIntegerField(verbose_name='page_no'),
        ),
    ]
