# Generated by Django 5.2.1 on 2025-05-20 19:08

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
            name='LeadSearchSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(default='New York', max_length=255)),
                ('keywords', models.CharField(default='office, gym, warehouse', max_length=255)),
                ('radius_miles', models.IntegerField(default=10)),
                ('lead_source', models.CharField(choices=[('google', 'Google Maps'), ('yelp', 'Yelp')], default='google', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lead_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
