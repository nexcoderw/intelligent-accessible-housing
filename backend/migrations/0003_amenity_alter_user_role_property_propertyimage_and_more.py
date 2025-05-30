# Generated by Django 5.0.4 on 2025-02-02 15:42

import backend.models
import django.db.models.deletion
import django.utils.timezone
import imagekit.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_user_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Amenities',
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('User', 'User')], max_length=30),
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('price_usd', models.IntegerField(blank=True, null=True)),
                ('price_rwf', models.IntegerField(blank=True, null=True)),
                ('capacity', models.IntegerField()),
                ('size', models.CharField(blank=True, max_length=255, null=True)),
                ('image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=backend.models.property_image_path)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amenities', models.ManyToManyField(blank=True, to='backend.amenity')),
            ],
            options={
                'verbose_name_plural': 'Properties',
            },
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=backend.models.property_add_on_image_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='backend.property')),
            ],
            options={
                'verbose_name_plural': 'Property Images',
            },
        ),
        migrations.CreateModel(
            name='PropertyReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('location', models.IntegerField(blank=True, default=5, null=True)),
                ('staff', models.IntegerField(blank=True, default=5, null=True)),
                ('cleanliness', models.IntegerField(blank=True, default=5, null=True)),
                ('value_for_money', models.IntegerField(blank=True, default=5, null=True)),
                ('comfort', models.IntegerField(blank=True, default=5, null=True)),
                ('facilities', models.IntegerField(blank=True, default=5, null=True)),
                ('free_wifi', models.IntegerField(blank=True, default=5, null=True)),
                ('status', models.BooleanField(blank=True, default=1, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.property')),
            ],
            options={
                'verbose_name_plural': 'Property Reviews',
            },
        ),
    ]
