# Generated by Django 4.2.3 on 2023-07-09 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('airport_code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('airport_name', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='EventsList',
            fields=[
                ('event_id', models.IntegerField(primary_key=True, serialize=False)),
                ('event_name', models.CharField(max_length=100)),
                ('rank', models.IntegerField()),
                ('location', models.CharField(max_length=100)),
                ('country_code', models.CharField(max_length=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WeatherInfo',
            fields=[
                ('event_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='eventsverse_app.eventslist')),
                ('temperature', models.FloatField()),
                ('humidity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='AvaliableFlights',
            fields=[
                ('flight_id', models.IntegerField(primary_key=True, serialize=False)),
                ('user_airport', models.CharField(max_length=3)),
                ('event_airport', models.CharField(max_length=3)),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('price', models.FloatField()),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventsverse_app.eventslist')),
            ],
        ),
    ]
