# Generated by Django 4.2.5 on 2023-10-06 04:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0002_delete_pollsresultpage"),
    ]

    operations = [
        migrations.RenameField(
            model_name="pollspagechoice",
            old_name="caption",
            new_name="choice_text",
        ),
    ]
