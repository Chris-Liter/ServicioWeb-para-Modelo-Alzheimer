# Generated by Django 5.1.4 on 2025-01-22 05:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Medico',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('dni', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=255)),
                ('age', models.IntegerField()),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pacientes', to='app.medico')),
            ],
        ),
        migrations.CreateModel(
            name='Radiografia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('imagen_base64', models.TextField()),
                ('explicacion', models.TextField()),
                ('probabilidad', models.TextField()),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('dementia_level', models.CharField(max_length=255)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='radiografias', to='app.paciente')),
            ],
        ),
    ]
