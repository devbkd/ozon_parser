from django.contrib import admin

from products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'description',
        'image_url',
        'discount',
    )
    search_fields = ('name',)
    list_filter = ('discount',)
    ordering = ('-price',)
