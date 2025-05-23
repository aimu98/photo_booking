# Generated by Django 5.2 on 2025-04-17 07:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo_booking_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='名前')),
                ('children_name', models.CharField(max_length=100, verbose_name='お子様のお名前')),
                ('email', models.EmailField(max_length=254, verbose_name='メールアドレス')),
                ('phone', models.CharField(max_length=15, verbose_name='電話番号')),
                ('date', models.DateField(verbose_name='予約日')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('plan', models.CharField(blank=True, max_length=100, null=True, verbose_name='プラン')),
                ('message', models.TextField(blank=True, verbose_name='ご不明点やご要望などお気軽にお書きください')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('date', 'start_time')},
            },
        ),
        migrations.DeleteModel(
            name='PhotoSession',
        ),
    ]
