from decimal import Decimal
from django.conf import settings
from core.models import Product
import json
from django.core.serializers.json import DjangoJSONEncoder

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        price = product.skidka_price if product.skidka_price is not None else product.price

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
    'price': str(price),
    'name': product.name,
    'image': product.images.first().image.url if product.images.exists() else '',
    'product_id': product.id,  # Добавляем ID продукта
    }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def save(self):
    # Преобразуем Decimal в строку для сериализации
        cart_to_save = {}
        for product_id, item in self.cart.items():
            cart_to_save[product_id] = {
            'quantity': item['quantity'],
            'price': str(item['price']),  # Decimal -> str
            'name': item['name'],
            'image': item.get('image', ''),
            'product_id': item['product_id']
        }
    
        self.session[settings.CART_SESSION_ID] = cart_to_save
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(product.id): product for product in products}
    
        for product_id, item in self.cart.items():
            item = item.copy()
            product = product_map.get(product_id)
            if product:
                item['product_id'] = product.id
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Полностью очищает корзину из сессии"""
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True  # Важно пометить сессию как измененную
        self.cart = {}  # Также очищаем локальную копию корзины