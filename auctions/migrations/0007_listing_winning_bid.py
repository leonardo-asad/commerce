# Generated by Django 4.0.3 on 2022-03-30 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_listing_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='winning_bid',
            field=models.PositiveIntegerField(null=True),
        ),
    ]