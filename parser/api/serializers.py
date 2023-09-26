from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'price', 'description', 'image_url', 'discount')


class ParsingRequestSerializer(serializers.Serializer):
    products_count = serializers.IntegerField(
        min_value=1, max_value=50, required=False, default=10
    )
