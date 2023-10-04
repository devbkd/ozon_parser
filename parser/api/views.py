from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)
from products.models import Product
from .serializers import ParsingRequestSerializer, ProductSerializer
from .tasks import parse_ozon_products


@api_view(['POST', 'GET'])
def products_list(request):
    if request.method == 'POST':
        serializer = ParsingRequestSerializer(data=request.data)
        if serializer.is_valid():
            products_count = serializer.validated_data.get('products_count')
            parse_ozon_products.delay(products_count=products_count)
            return Response(
                {
                    'error': False,
                    'message': f'Parsing {products_count} products started.',
                },
                status=HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        products_all = Product.objects.all()
        serializer = ProductSerializer(products_all, many=True)
        return Response(
            {'error': False, 'message': 'OK', 'payload': serializer.data},
            status=HTTP_200_OK,
        )


@api_view(['GET'])
def product_detail(request, product_id: int):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'error': True, 'message': 'Product not found.', 'payload': None},
            status=HTTP_200_OK,
        )

    serializer = ProductSerializer(product)
    return Response(
        {'error': False, 'message': 'OK', 'payload': serializer.data},
        status=HTTP_200_OK,
    )
