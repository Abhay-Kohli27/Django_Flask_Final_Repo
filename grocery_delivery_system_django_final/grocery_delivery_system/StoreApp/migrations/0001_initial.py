# Generated by Django 5.2 on 2025-05-06 02:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('store_id', models.AutoField(primary_key=True, serialize=False)),
                ('store_name', models.CharField(max_length=20, unique=True)),
                ('store_category', models.CharField(max_length=20)),
                ('store_description', models.TextField(max_length=200)),
                ('store_logo', models.ImageField(null=True, upload_to='store_logo/')),
                ('store_legal_business_name', models.CharField(max_length=40)),
                ('tax_number', models.CharField(max_length=20)),
                ('owner_name', models.CharField(max_length=20)),
                ('business_email', models.EmailField(max_length=254, unique=True)),
                ('store_address', models.TextField()),
                ('business_documentation', models.ImageField(null=True, upload_to='store_documentation/')),
                ('is_approved', models.BooleanField()),
                ('opening_time', models.TimeField(null=True)),
                ('closing_time', models.TimeField(null=True)),
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
