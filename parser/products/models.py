from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название')
    price = models.IntegerField(verbose_name='Цена')
    description = models.TextField(verbose_name='Описание')
    image_url = models.URLField(null=True, verbose_name='Изображение товара')
    discount = models.CharField(max_length=200, verbose_name='Скидка')

    def __str__(self):
        return self.name
