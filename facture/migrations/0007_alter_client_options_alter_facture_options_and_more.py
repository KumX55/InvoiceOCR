# Generated by Django 4.0.2 on 2022-03-23 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('facture', '0006_alter_facture_options_client_creation_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterModelOptions(
            name='facture',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterModelOptions(
            name='fournisseur',
            options={'ordering': ['-pk']},
        ),
        migrations.AlterModelOptions(
            name='produit',
            options={'ordering': ['-pk']},
        ),
    ]
