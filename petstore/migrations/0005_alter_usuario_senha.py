# Generated by Django 4.2.16 on 2024-10-05 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petstore', '0004_alter_usuario_nome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='senha',
            field=models.CharField(max_length=200),
        ),
    ]
