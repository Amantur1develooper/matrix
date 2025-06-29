from django.shortcuts import render,get_object_or_404
from django.core.mail import EmailMessage, BadHeaderError
from smtplib import SMTPException
from django.views.decorators.http import require_POST

from core.tg import send_broadcast
from .models import Category, KaruselImage, Letter, Product, ProductImage
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives  # Используем этот класс для HTML писем
from django.conf import settings
from smtplib import SMTPException
from django.core.mail import BadHeaderError
# Create your views here.
from django.http import HttpResponse
from core.models import Order
from core.cart import Cart
# from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .forms import OrderCreateForm
from .models import OrderItem
from django.contrib.sessions.backends.db import SessionStore
from django.db import models
from django.core.mail import send_mail
from django.http import HttpResponse
# from core.models import EmailRecipient
from django.db.models import Q
from .models import Product  # Предполагая, что у вас есть модель Product
from .models import Product, ProductImage
from celery import shared_task
from django.core.mail import send_mail
categories = Category.objects.all()
@shared_task
def send_email_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'onlineprintern1@gmail.com',  # отправитель
        recipient_list,
        fail_silently=False,
    )                                   
from django.db.models import Q

def dostavka_oplata(request):
    return render(request, 'dostavka_oplata.html',{"categories": categories,})

def warranty(request):
    return render(request, 'warranty.html',{"categories": categories,})

# views.py
def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        message = request.POST.get('message')
        Letter.objects.create(
            name=name,
            number_phone=phone,
            pochta=email,
            cat=message
        )
        # Обработка данных (отправка email, сохранение в БД и т.д.)
        return redirect('contacts')  # Или сообщение об успешной отправке
    
    return render(request, 'contacts.html',{"categories": categories,})


def main_sevice(request):
    return render(request, 'main_sevice.html',{"categories": categories,})


def about_us(request):
    return render(request, 'about_us.html',{"categories": categories,})


def home(request):
    query = request.GET.get('q', '')
    search_results = []
    
    # Поиск с подсказками (AJAX запрос)
    if query and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Ищем товары, где название начинается с запроса (более релевантные)
        starts_with = Product.objects.filter(
            Q(name__istartswith=query)
        ).prefetch_related('images').distinct()[:5]
        
        # Если мало результатов, ищем товары, содержащие запрос
        contains = []
        if starts_with.count() < 5:
            contains = Product.objects.filter(
                Q(name__icontains=query) & ~Q(name__istartswith=query)
            ).prefetch_related('images').distinct()[:5 - starts_with.count()]
        
        search_results = list(starts_with) + list(contains)
        return render(request, 'shop/includes/search_suggestions.html', {
            'search_results': search_results,
            'search_query': query
        })
    
    # Обычный поиск при нажатии Enter/поиске
    if query:
        search_results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).prefetch_related('images').distinct()
    
    categories = Category.objects.filter(parent__isnull=True)
    karusel = KaruselImage.objects.all()
    top_products = Product.objects.filter(is_top=True)[:4]
    products = Product.objects.all().filter(is_top=False)
    
    context = {
        'category_none':True,
        "categories": categories,
        'karusel': karusel,
        'search_results': search_results,
        'search_query': query,
        'top_products': top_products,
        'products':products
    }
    
    return render(request, "home.html", context)


def sales_view(request):
    # Получаем товары со скидкой (где skidka_price не None)
    discounted_products = Product.objects.filter(skidka_price__isnull=False)
    
    context = {
        'discounted_products': discounted_products,
        'title': 'Товары со скидкой',
        "categories": categories,
    }
    return render(request, 'sales.html', context)
# def home(request):
#     query = request.GET.get('q', '')
#     products = []
#     #
    
#     if query:
#         products = Product.objects.filter(
#             Q(name__icontains=query) | 
#             Q(description__icontains=query)
#         ).prefetch_related('images').distinct()[:10]
    
#     categories = Category.objects.filter(parent__isnull=True)
#     karusel = KaruselImage.objects.all()
#     products = Product.objects.all()
#     context = {
#         "categories": categories,
#         'karusel': karusel,
#         'search_results': products,
#         'search_query': query,
#         'products':products,
#         "top_products":products
#     }
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return render(request, 'search_results.html', {'search_results': products})
    
#     return render(request, "home.html", context)

from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Category, Product

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    # Получаем все товары категории + товары из подкатегорий
    subcategories = category.get_descendants(include_self=True)
    
    # Оптимизированный запрос с prefetch_related для изображений
    products = Product.objects.filter(
        categories__in=subcategories
    ).prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.all(), to_attr='prefetched_images')
    ).distinct()
    
    # Получаем иерархию категорий для хлебных крошек
    breadcrumbs = []
    parent = category.parent
    while parent:
        breadcrumbs.append(parent)
        parent = parent.parent
    breadcrumbs.reverse()
    
    # Получаем подкатегории с предварительной загрузкой их товаров
    subcategories_with_counts = category.children.annotate(product_count=models.Count('product', distinct=True))
    
    return render(request, 'shop/category.html', {
        'category_none':True,
        'category': category,
        'products': products,
        'breadcrumbs': breadcrumbs,
        'subcategories': subcategories_with_counts,
        'current_path': request.path
    })
    
    
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Product, Category



def product_detail(request, slug):
    # Получаем товар с оптимизированными запросами
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.all()),
            Prefetch('categories', queryset=Category.objects.all())
        ),
        slug=slug
    )
    
    # Получаем похожие товары (из тех же категорий)
    related_products = Product.objects.filter(
        categories__in=product.categories.all()
    ).exclude(
        pk=product.pk
    ).distinct().order_by('?')[:3]  # Берем 4 случайных товара
    
    # Получаем топовые товары (кроме текущего)
    top_products = Product.objects.filter(
        is_top=True
    ).exclude(
        pk=product.pk
    ).order_by('-created_at')[:2]  # Берем 4 последних топовых товара
    
    # Хлебные крошки (берем первую категорию)
    breadcrumbs = []
    main_category = None
    if product.categories.exists():
        main_category = product.categories.first()
        parent = main_category.parent
        while parent:
            breadcrumbs.append(parent)
            parent = parent.parent
        breadcrumbs.reverse()
        breadcrumbs.append(main_category)
    categories = Category.objects.all()
    return render(request, 'shop/product_detail.html', {
        "categories": categories,
        'product': product,
        'related_products': related_products,
        'top_products': top_products,
        'breadcrumbs': breadcrumbs,
        'main_category': main_category
    })
    
def remontpk(request):
    return render(request, 'shop/service/remontpk.html',{"categories": categories,} )
def remonorg(request):
    return render(request, 'shop/service/remontorg.html',{"categories": categories,} )
def install_settings(request):
    return render(request, 'shop/service/install_settings.html',{"categories": categories,} )
def org_obsluj(request):
    return render(request, 'shop/service/org_obsluj.html',{"categories": categories,} )

# def product_detail(request, slug):
#     # Получаем товар с оптимизированными запросами
#     product = get_object_or_404(
#         Product.objects.prefetch_related(
#             Prefetch('images', queryset=ProductImage.objects.all()),
#             Prefetch('categories', queryset=Category.objects.all())
#         ),
#         slug=slug
#     )
    
#     # Получаем связанные товары (из тех же категорий)
#     related_products = Product.objects.filter(
#         categories__in=product.categories.all()
#     ).exclude(
#         pk=product.pk
#     ).distinct()[:4]  # Ограничиваем 4 товарами
    
#     # Хлебные крошки (берем первую категорию)
#     breadcrumbs = []
#     if product.categories.exists():
#         main_category = product.categories.first()
#         parent = main_category.parent
#         while parent:
#             breadcrumbs.append(parent)
#             parent = parent.parent
#         breadcrumbs.reverse()
#         breadcrumbs.append(main_category)
    
#     return render(request, 'shop/product_detail.html', {
#         'product': product,
#         'related_products': related_products,
#         'breadcrumbs': breadcrumbs,
#         'main_category': main_category if product.categories.exists() else None
#     })
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .cart import Cart
# from shop.models import Product, Category
from django.http import JsonResponse

def cart_detail(request):
    cart = CartDB(request)
    categories = Category.objects.all()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Для AJAX-запросов возвращаем JSON
        return JsonResponse({
            'total_items': len(cart),
            'total_price': cart.get_total_price()
        })
    
    return render(request, 'shop/cart.html', {'cart': cart, 'categories': categories})
# def cart_detail(request):
#     cart = Cart(request)
#     categories = Category.objects.all()
#     return render(request, 'shop/cart.html', {'cart': cart, 'categories': categories})
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from core.models import Product
from .cart import CartDB  # Используем новую реализацию
# def cart_add(request, product_id):
#     cart = CartDB(request)
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == 'POST':
#         quantity = int(request.POST.get('quantity', 1))
#         update_quantity = request.POST.get('update_quantity') == 'true'
        
#         cart.add(product, quantity, update_quantity)
        
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'status': 'success',
#                 'total_price': str(cart.get_total_price())
#             })
        
#         return redirect('cart_detail')
    
#     return redirect('cart_detail')


# @require_POST
# def cart_add(request, product_id):
#     cart = CartDB(request)
#     product = get_object_or_404(Product, id=product_id)


#     try:
#         quantity = int(request.POST.get('quantity', 1))
#         update_quantity = request.POST.get('update_quantity') == 'true'

#         cart.add(
#             product=product,
#             quantity=quantity,
#             update_quantity=update_quantity
#         )

#         return JsonResponse({
#             'status': 'success',
#             'total_items': len(cart),
#             'total_price': str(cart.get_total_price()),
#             'item_price': str(product.skidka_price if product.skidka_price else product.price),
#             'product_id': product_id
#         })

#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)
def cart_add(request, product_id):
    cart = CartDB(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            update_quantity = request.POST.get('update_quantity') == 'true'

            cart.add(
                product=product,
                quantity=quantity,
                update_quantity=update_quantity
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'total_items': len(cart),
                    'total_price': str(cart.get_total_price()),
                    'item_price': str(product.skidka_price or product.price),
                })

            return redirect('cart_detail')

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
            raise

# def cart_add(request, product_id):
    
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == 'POST':
#         try:
#             quantity = int(request.POST.get('quantity', 1))
#             update_quantity = request.POST.get('update_quantity') == 'true'
            
#             cart.add(
#                 product=product,
#                 quantity=quantity,
#                 update_quantity=update_quantity
#             )
            
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'status': 'success',
#                     'total_items': cart.__len__(),
#                     'total_price': str(cart.get_total_price()),
#                     'item_price': str(product.price),  # Добавляем цену товара
#                 })
            
#             return redirect('cart_detail')
            
#         except Exception as e:
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': str(e)
#                 }, status=500)
#             raise
# def cart_add(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == 'POST':
#         form = CartAddProductForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             cart.add(
#                 product=product,
#                 quantity=cd['quantity'],
#                 update_quantity=cd['update']
#             )
            
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({
#                     'total_items': cart.__len__(),
#                     'total_price': str(cart.get_total_price())
#                 })
#     return redirect('cart_detail')

# def cart_add(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     quantity = int(request.POST.get('quantity', 1))
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         # AJAX запрос
#         cart.add(product, quantity, update_quantity=True)
#         return JsonResponse({
#             'success': True,
#             'total_price': cart.get_total_price(),
#             'quantity': sum(item['quantity'] for item in cart)
#         })
    
#     cart.add(product, quantity)
#     return redirect('cart_detail')



def cart_remove2(request, product_id):
    cart = CartDB(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

from django.views.decorators.http import require_POST

# @require_POST
# def cart_remove(request, product_id):
#     cart = CartDB(request)
#     product = get_object_or_404(Product, id=product_id)
#     cart.remove(product)
#     return JsonResponse({
#         'status': 'success',
#         'total_items': len(cart),
#         'total_price': str(cart.get_total_price())
#     })
# @require_POST
def cart_remove(request, product_id):
    cart = CartDB(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart_detail")
    return JsonResponse({'status': 'ok'})
# @require_POST
# def cart_remove(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     cart.remove(product)
#     return JsonResponse({'status': 'ok'})
from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from .models import Product

# def cart_add(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     quantity = int(request.POST.get('quantity', 1))
    
#     # Проверяем наличие товара
#     if product.stock >= quantity:
#         cart.add(product, quantity)
#         return redirect('cart_detail')
#     else:
#         # Можно добавить сообщение об ошибке
#         return redirect('product_detail', slug=product.slug)

# def cart_remove(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     cart.remove(product)
#     return redirect('cart_detail')

# def cart_detail(request):
#     cart = Cart(request)
#     carts = Category.objects.all()
#     return render(request, 'shop/cart.html', {'categories':carts,'cart': cart})


from django.shortcuts import render, get_object_or_404, redirect
from .cart import CartDB
from .forms import OrderCreateForm
from .models import OrderItem, Product

from .models import Category  # если используешь категории

def checkout(request):
    cart = CartDB(request)
    # categories = Category.objects.all()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid() and len(cart) > 0:
            order = form.save(commit=False)
            
            if request.user.is_authenticated:
                order.user = request.user
            
            order.total = cart.get_total_price()
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                
       
        
        # Текстовый вариант письма
            text_message = render_to_string('shop/email/order_email.txt', {
            'order': order,
            'cart': cart,
            })
            send_broadcast(text_message)
            # send_order_email(order, cart)
            cart.clear()

            categories = Category.objects.all()
            return render(request, 'shop/order_created.html', {
                'order': order,
                "categories": categories
            })
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'email': request.user.email,
                'full_name': request.user.get_full_name(),
            }
        form = OrderCreateForm(initial=initial)
    
    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'form': form,
        # 'categories': categories
    })

# def checkout(request):
#     cart = Cart(request)
    
#     if request.method == 'POST':
#         form = OrderCreateForm(request.POST)
#         if form.is_valid() and cart:
#             order = form.save(commit=False)
            
#             if request.user.is_authenticated:
#                 order.user = request.user
            
#             order.total = cart.get_total_price()
#             order.save()
            
#             # Сохраняем товары заказа
#             for item in cart:
#                 product = Product.objects.get(id=item['product_id'])  # Получаем продукт по ID
#                 OrderItem.objects.create(
#                     order=order,
#                     product=product,
#                     price=item['price'],
#                     quantity=item['quantity']
#                 )
            
#             send_order_email(order, cart)
#             cart.clear()
            
#             return render(request, 'shop/order_created.html', {'order': order, "categories": categories})
#     else:
#         initial = {}
#         if request.user.is_authenticated:
#             initial = {
#                 'email': request.user.email,
#                 'full_name': request.user.get_full_name(),
#             }
#         form = OrderCreateForm(initial=initial)
    
#     return render(request, 'shop/checkout.html', {
#         'cart': cart,
#         'form': form,
#     })
# views.py


# from django.core.exceptions import BadHeaderError

def send_order_email(order, cart):
    try:
        subject = f"Новый заказ #{order.id}"
        
        # Текстовый вариант письма
        text_message = render_to_string('shop/email/order_email.txt', {
            'order': order,
            'cart': cart,
        })
        
        # HTML вариант письма
        html_message = render_to_string('shop/email/order_email.html', {
            'order': order,
            'cart': cart,
        })
        
        # Создаем письмо
        # email = EmailMultiAlternatives(
        #     subject=,
        #     body=,  # Текстовая версия
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #      # Клиенту
        #     cc=settings.ORDER_EMAIL_RECIPIENTS,  # Копии менеджерам
        # )
        send_email_task(subject, text_message, ['amanerkinov9@gmail.com'])
        # email.attach_alternative(html_message, "text/html")  # HTML версия
        # email.send()
        
    except BadHeaderError:
        # Логирование ошибки неверного заголовка
        print("Ошибка в заголовке письма")
    except SMTPException as e:
        # Логирование ошибки SMTP
        print(f"Ошибка отправки email: {e}")
    except Exception as e:
        # Логирование других ошибок
        print(f"Неожиданная ошибка: {e}")



# def test_email(request):
#     send_mail(
#         'Тестовое письмо из Django',
#         'Это тестовое сообщение, отправленное через Mailtrap.',
#         DEFAULT_FROM_EMAIL,
#         ['amanerkinov9@gmail.com'],  # Укажите реальный email для теста
#         fail_silently=False,
#     )
#     return HttpResponse("Тестовое письмо отправлено!")


        
def test_email(request):
    try:
       
        # Создаем тестовый заказ и корзину
    
        # Тестовая корзина
        session = SessionStore()
        session.create()
        request.session = session
        cart = Cart(request)
        # Добавьте тестовые товары в корзину если нужно
        
        # Тестовый заказ
        order = Order.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone="+1234567890",
            address="Test Address",
            total=100
        )
        
        # Отправка письма
        send_order_email(order, cart)
        print("_______________________go________________________")
        return HttpResponse("Тестовое письмо отправлено!")
    except Exception as e:
        return HttpResponse(f"Ошибка: {str(e)}")