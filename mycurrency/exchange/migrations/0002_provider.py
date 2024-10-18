# Generated by Django 5.1.2 on 2024-10-17 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('priority', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
