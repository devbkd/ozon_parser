import json
import logging
import tls_client

from parser.celery import app
from products.models import Product


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_file = 'parser.log'
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=10 * 1024 * 1024, backupCount=5
)  # Максимум 10 МБ, 5 ротаций
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def get_all_products():
    url = 'https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=/seller/proffi-1/products/'

    session = tls_client.Session(
        client_identifier="chrome112", random_tls_extension_order=True
    )
    response = session.get(url)
    data = response.json()
    return data


@app.task
def parse_ozon_products(products_count=10):
    products_input = get_all_products()
    data = products_input.get('widgetStates', {}).get(
        'searchResultsV2-3050041-default-1', []
    )
    if not data:
        print("Нет данных в структуре JSON.")
        return
    data = json.loads(data)

    for item in data['items']:
        if not isinstance(item, dict):
            continue
        main_state = item.get('mainState', [])
        if len(main_state) > 2 and 'atom' in main_state[2]:
            name = next(
                (
                    item['atom']['textAtom']['text']
                    for item in main_state
                    if 'id' in item and item['id'] == 'name'
                ),
                None,
            )
        else:
            name = ''
        try:
            price_data = item['atom']['priceV2']['price']
        except (KeyError, IndexError):
            description = None
        if price_data:
            price = price_data[0].get('text', '')
            discount = main_state[0].get('atom').get('priceV2').get('discount')
        else:
            price = ''
            discount = ''
        try:
            description = item['topAttributes']['atom']['textAtom']['text']
        except (KeyError, IndexError):
            description = None
        try:
            image_url = item['tileImage']['items'][0]['image']['link']
        except (KeyError, IndexError):
            image_url = None
        Product.objects.create(
            name=name,
            price=price,
            description=description,
            image_url=image_url,
            discount=discount,
        )

    logger.info("Данные успешно сохранены в базе данных.")


parse_ozon_products()
