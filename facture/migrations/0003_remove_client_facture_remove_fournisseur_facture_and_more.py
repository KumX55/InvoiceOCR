# Generated by Django 4.0.2 on 2022-03-15 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facture', '0002_facture_creation_date_facture_ref_fac_facture_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='facture',
        ),
        migrations.RemoveField(
            model_name='fournisseur',
            name='facture',
        ),
        migrations.AddField(
            model_name='facture',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facture.client'),
        ),
        migrations.AddField(
            model_name='facture',
            name='fournisseur',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facture.fournisseur'),
        ),
    ]
