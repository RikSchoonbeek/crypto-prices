# Generated by Django 2.2.1 on 2019-05-05 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoCurrency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TickerSymbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=8)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cryptodata.CryptoCurrency')),
            ],
        ),
        migrations.AddField(
            model_name='cryptocurrency',
            name='exchanges',
            field=models.ManyToManyField(to='cryptodata.Exchange'),
        ),
    ]