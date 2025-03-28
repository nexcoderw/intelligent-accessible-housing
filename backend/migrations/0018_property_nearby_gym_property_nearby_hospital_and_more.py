# Generated by Django 5.0.4 on 2025-03-19 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_category_created_at_category_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='nearby_gym',
            field=models.CharField(blank=True, help_text='Nearby gym or fitness center', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='nearby_hospital',
            field=models.CharField(blank=True, help_text='Nearby hospital name or details', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='nearby_market',
            field=models.CharField(blank=True, help_text='Nearby market name or details', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='nearby_park',
            field=models.CharField(blank=True, help_text='Nearby park or recreational area', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='nearby_school',
            field=models.CharField(blank=True, help_text='Nearby school name or details', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='nearby_transport',
            field=models.CharField(blank=True, help_text='Nearby transport options or station', max_length=255, null=True),
        ),
    ]
