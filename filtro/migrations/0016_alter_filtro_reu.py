# Generated by Django 4.1 on 2023-08-11 15:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("filtro", "0015_alter_filtro_reu"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filtro",
            name="reu",
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]