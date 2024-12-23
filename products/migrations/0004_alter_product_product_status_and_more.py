# Generated by Django 4.2.11 on 2024-12-19 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_product_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.CharField(choices=[('disabled', 'Disabled'), ('rejected', 'Rejected'), ('published', 'Published'), ('in_review', 'IN Review'), ('draft', 'Draft')], default='in_review', max_length=10),
        ),
        migrations.AlterField(
            model_name='productsreviews',
            name='rating',
            field=models.ImageField(choices=[(1, '★✩✩✩✩'), (3, '★★★✩✩'), (5, '★★★★★'), (2, '★★✩✩✩'), (4, '★★★★✩')], default=None, upload_to=''),
        ),
    ]
