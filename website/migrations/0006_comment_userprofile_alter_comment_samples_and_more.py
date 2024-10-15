# Generated by Django 4.2.16 on 2024-10-15 03:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_alter_sample_audiofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='userProfile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.userprofile'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='samples',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.sample'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='userPhoto',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
