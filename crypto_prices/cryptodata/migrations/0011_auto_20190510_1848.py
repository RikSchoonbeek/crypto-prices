# Generated by Django 2.2.1 on 2019-05-10 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cryptodata', '0010_auto_20190510_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickersymbol',
            name='symbol',
            field=models.CharField(max_length=8),
        ),
        migrations.AlterUniqueTogether(
            name='tickersymbol',
            unique_together={('symbol', 'currency')},
        ),
    ]