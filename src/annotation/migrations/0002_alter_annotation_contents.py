# Generated by Django 5.0 on 2024-03-16 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='contents',
            field=models.TextField(null=True, verbose_name='contents'),
        ),
    ]