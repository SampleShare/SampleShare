# Generated by Django 5.1.1 on 2024-10-28 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_remove_genre_samples_sample_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='userProfiles',
            field=models.ManyToManyField(blank=True, to='website.userprofile'),
        ),
    ]