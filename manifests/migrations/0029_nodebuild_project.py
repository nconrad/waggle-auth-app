# Generated by Django 4.2.5 on 2023-09-29 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0007_alter_user_is_approved"),
        ("manifests", "0028_alter_nodebuild_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="nodebuild",
            name="project",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="app.project",
            ),
        ),
    ]