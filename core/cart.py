from decimal import Decimal
from django.conf import settings
from core.models import Product
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import Cart, CartItem
from core.models import Product

class CartDB:
    def __init__(self, request):
        self.session = request.session
        self.session_key = request.session.session_key
        if not self.session_key:
            self.session.save()
            self.session_key = self.session.session_key

        cart, created = Cart.objects.get_or_create(session_key=self.session_key)
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        cart_item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            defaults={'quantity': quantity}
        )
    
        if not created:
            if update_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
        
        # Проверяем, чтобы количество не было отрицательным
            if cart_item.quantity < 1:
                cart_item.quantity = 1
            
            cart_item.save()
    
        return cart_item

    def remove(self, product):
        CartItem.objects.filter(cart=self.cart, product=product).delete()

    def __iter__(self):
        for item in self.cart.items.select_related('product'):
            product = item.product
            price = product.skidka_price if product.skidka_price else product.price
            yield {
                'product': product,
                'quantity': item.quantity,
                'price': price,
                'total_price': price * item.quantity
            }

    def __len__(self):
        return sum(item.quantity for item in self.cart.items.all())

    def get_total_price(self):
        total = 0
        for item in self.cart.items.select_related('product'):
            price = item.product.skidka_price if item.product.skidka_price else item.product.price
            total += price * item.quantity
        return total

    def clear(self):
        self.cart.items.all().delete()

# class Cart:
#     def __init__(self, request):
#         self.session = request.session
#         cart = self.session.get(settings.CART_SESSION_ID)
#         if not cart:
#             cart = self.session[settings.CART_SESSION_ID] = {}
#         self.cart = cart

#     def add(self, product, quantity=1, update_quantity=False):
#         product_id = str(product.id)
#         price = product.skidka_price if product.skidka_price is not None else product.price

#         if product_id not in self.cart:
#             self.cart[product_id] = {
#                 'quantity': 0,
#                 'price': str(price),
#                 'name': product.name,
#                 'image': product.images.first().image.url if product.images.exists() else '',
#                 'product_id': product_id,  # Добавляем ID продукта
#                 }
        
#         if update_quantity:
#             self.cart[product_id]['quantity'] = quantity
#         else:
#             self.cart[product_id]['quantity'] += quantity
            
#         self.save()

#     def save(self):
#     # Преобразуем Decimal в строку для сериализации
#         cart_to_save = {}
#         for product_id, item in self.cart.items():
#             cart_to_save[product_id] = {
#             'quantity': item['quantity'],
#             'price': str(item['price']),  # Decimal -> str
#             'name': item['name'],
#             'image': item.get('image', ''),
#             'product_id': item['product_id']
#         }
    
#         self.session[settings.CART_SESSION_ID] = cart_to_save
#         self.session.modified = True

#     def remove(self, product):
#         product_id = str(product.id)
#         if product_id in self.cart:
#             del self.cart[product_id]
#             self.save()

#     def __iter__(self):
#         product_ids = self.cart.keys()
#         products = Product.objects.filter(id__in=product_ids)
#         product_map = {str(product.id): product for product in products}
    
#         for product_id, item in self.cart.items():
#             item = item.copy()
#             product = product_map.get(product_id)
#             if product:
#                 item['product_id'] = product_id
#                 item['price'] = Decimal(item['price'])
#                 item['total_price'] = item['price'] * item['quantity']
#                 yield item

#     def __len__(self):
#         return sum(item['quantity'] for item in self.cart.values())

#     def get_total_price(self):
#         return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

#     def clear(self):
#         """Полностью очищает корзину из сессии"""
#         if settings.CART_SESSION_ID in self.session:
#             del self.session[settings.CART_SESSION_ID]
#             self.session.modified = True  # Важно пометить сессию как измененную
#         self.cart = {}  # Также очищаем локальную копию корзины