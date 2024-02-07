# Generated by Django 4.2.2 on 2023-10-25 14:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_merge_0002_alter_category_image_0002_review_is_valid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=3,
                null=True,
                verbose_name="rating",
            ),
        ),
    ]