# Generated by Django 4.2.5 on 2023-10-02 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repository_id', models.IntegerField()),
                ('dblp_id', models.CharField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('external_name', models.CharField(max_length=200)),
            ],
        ),
    ]
