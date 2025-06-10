from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import KaruselImage, Letter, Product, Category, ProductImage, Order, OrderItem
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, Category, ProductImage, Order, OrderItem, EmailRecipient
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
# Форма для удобного выбора категорий
from .forms import ProductAdminForm
# Inline для изображений товара
from .models import ProductSpecification, ProductSpecificationValue
admin.site.site_header = "Админ-панель"
admin.site.register(EmailRecipient)
admin.site.register(KaruselImage)


    
    
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"
admin.site.register(Letter)

# Inline для позиций заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_price')
    fields = ('product', 'quantity', 'price', 'total_price')
    
    def total_price(self, obj):
        return obj.price * obj.quantity
    total_price.short_description = "Сумма"

# Категории с древовидным отображением
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'product_count')
    list_filter = ('parent',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = "Товаров"
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Prefetch
from .models import Product, ProductSpecification, ProductSpecificationValue, ProductImage
from .forms import ProductAdminForm

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_preview', 'is_main')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = "Превью"

class ProductSpecificationValueInline(admin.TabularInline):
    model = ProductSpecificationValue
    extra = 1
    fields = ('specification', 'value')
    autocomplete_fields = ['specification']

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'values_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)

    def values_count(self, obj):
        return obj.values.count()
    values_count.short_description = "Использований"

@admin.register(ProductSpecificationValue)
class ProductSpecificationValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'specification', 'value')
    list_filter = ('specification',)
    search_fields = ('product__name', 'value', 'specification__name')
    autocomplete_fields = ('product', 'specification')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductSpecificationValueInline, ProductImageInline]
    filter_horizontal = ('categories',)
    
    list_display = (
        'name', 
        'categories_list', 
       
        'stock_status', 
        'barcode', 
        'qr_code_preview', 
        'image_preview',
        'is_top_display'
    )
    list_filter = ('categories', 'is_top', 'created_at')
    search_fields = ('name', 'barcode', 'description', 'specifications__value')
    # list_editable = ( 'is_top_display',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('qr_code_preview', 'created_at', 'updated_at', 'barcode_display')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'categories', 'description')
        }),
        ('Цена и наличие', {
            'fields': (
                ('price', 'skidka_price'), 
                'stock', 
                'is_top'
            )
        }),
        ('Коды', {
            'fields': (
                'barcode_display',
                'qr_code', 
                'qr_code_preview'
            ),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_top_action', 'remove_top_action', 'generate_barcodes']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch('categories'),
            Prefetch('images'),
            Prefetch('specifications')
        )

    def categories_list(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    categories_list.short_description = "Категории"

    def price_display(self, obj):
        if obj.skidka_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{}</span><br>{} сом',
                obj.price,
                obj.skidka_price
            )
        return f"{obj.price} сом"
    price_display.short_description = "Цена"
    price_display.admin_order_field = 'price'

    def is_top_display(self, obj):
        return obj.is_top
    is_top_display.short_description = "Топ"
    is_top_display.boolean = True

    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
            text = f"{obj.stock} шт"
        elif obj.stock > 0:
            color = 'orange'
            text = f"{obj.stock} шт"
        else:
            color = 'red'
            text = "Нет в наличии"
        return format_html('<span style="color: {};">{}</span>', color, text)
    stock_status.short_description = "Наличие"

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.qr_code.url)
        return "-"
    qr_code_preview.short_description = "QR код"

    def image_preview(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html('<img src="{}" style="max-height: 50px;" />', first_image.image.url)
        return "-"
    image_preview.short_description = "Изображение"

    def barcode_display(self, obj):
        return obj.barcode or "Не задан"
    barcode_display.short_description = "Штрих-код"

    def make_top_action(self, request, queryset):
        updated = queryset.update(is_top=True)
        self.message_user(request, f"{updated} товаров помечено как Топ")
    make_top_action.short_description = "Пометить как Топ"

    def remove_top_action(self, request, queryset):
        updated = queryset.update(is_top=False)
        self.message_user(request, f"{updated} товаров убрано из Топ")
    remove_top_action.short_description = "Убрать из Топ"

    def generate_barcodes(self, request, queryset):
        # Здесь может быть логика генерации штрих-кодов
        self.message_user(request, "Генерация штрих-кодов не реализована")
    generate_barcodes.short_description = "Сгенерировать штрих-коды"

# Улучшенный админ для заказов
# Улучшенный админ для заказов
# Улучшенный админ для заказов
admin.site.register(Order)
admin.site.register(OrderItem)

# admin.site.register(ProductSpecificationValue)
# class ProductSpecificationValueInline(admin.TabularInline):
#     model = ProductSpecificationValue
#     extra = 1
# @admin.register(ProductSpecification)
# class ProductSpecificationAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug')
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields = ('name',)
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     inlines = [ProductSpecificationValueInline]
#     form = ProductAdminForm
#     filter_horizontal = ('categories',)  # Для ManyToManyField
    
#     list_display = ('name', 'categories_list', 'price', 'stock_status', 'barcode', 'qr_code_preview', 'image_preview')
#     list_filter = ('categories', 'is_top')
#     search_fields = ('name', 'barcode', 'description')
#     list_editable = ('price',)
#     prepopulated_fields = {'slug': ('name',)}
#     readonly_fields = ('barcode', 'qr_code_preview', 'created_at', 'updated_at')
    
#     fieldsets = (
#         (None, {
#             'fields': ('name', 'slug', 'categories', 'description')
#         }),
#         ('Цена и наличие', {
#             'fields': ('price','skidka_price', 'stock', 'is_top')
#         }),
#         ('Коды', {
#             'fields': ('barcode', 'qr_code', 'qr_code_preview')
#         }),
#         ('Даты', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     inlines = [ProductImageInline]
#     actions = ['make_top_action', 'remove_top_action']
    
#     def categories_list(self, obj):
#         return ", ".join([c.name for c in obj.categories.all()])  # Исправлено на categories
#     categories_list.short_description = "Категории"
    
#     # Остальные методы остаются без изменений
#     def make_top_action(self, request, queryset):
#         queryset.update(is_top=True)
#     make_top_action.short_description = "Пометить как Топ 5"
    
#     def remove_top_action(self, request, queryset):
#         queryset.update(is_top=False)
#     remove_top_action.short_description = "Убрать из Топ 5"
    
#     def stock_status(self, obj):
#         if obj.stock > 10:
#             color = 'green'
#             text = f"{obj.stock} шт"
#         elif obj.stock > 0:
#             color = 'orange'
#             text = f"{obj.stock} шт"
#         else:
#             color = 'red'
#             text = "Нет в наличии"
#         return format_html('<span style="color: {};">{}</span>', color, text)
#     stock_status.short_description = "Наличие"
    
#     def qr_code_preview(self, obj):
#         if obj.qr_code:
#             return format_html('<img src="{}" style="max-height: 50px;" />', obj.qr_code.url)
#         return "-"
#     qr_code_preview.short_description = "QR код"
    
#     def image_preview(self, obj):
#         first_image = obj.images.first()
#         if first_image:
#             return format_html('<img src="{}" style="max-height: 50px;" />', first_image.image.url)
#         return "-"
#     image_preview.short_description = "Изображение"
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer_info', 'total', 'status', 'created_at', 'order_actions')
#     list_filter = ('status', 'created_at')
#     search_fields = ('full_name', 'phone', 'address')
#     readonly_fields = ('created_at', 'total')
#     inlines = [OrderItemInline]
    
#     # Правильное объявление actions как списка строк
#     actions = ['mark_as_processed', 'mark_as_completed', 'mark_as_cancelled']
    
#     def customer_info(self, obj):
#         return format_html(
#             '<strong>{}</strong><br>{}<br>{}',
#             obj.full_name,
#             obj.phone,
#             obj.address
#         )
#     customer_info.short_description = "Клиент"
    
#     def order_actions(self, obj):
#         return format_html(
#         '<a href="{}" class="button">Просмотр</a>',
#         reverse('admin:core_order_change', args=[obj.id])
#     )
#     order_actions.short_description = "Действия"
    
#     def mark_as_processed(self, request, queryset):
#         queryset.update(status='processing')
#     mark_as_processed.short_description = "Перевести в обработку"
    
#     def mark_as_completed(self, request, queryset):
#         queryset.update(status='completed')
#     mark_as_completed.short_description = "Завершить заказы"
    
#     def mark_as_cancelled(self, request, queryset):
#         queryset.update(status='cancelled')
#     mark_as_cancelled.short_description = "Отменить заказы"
# Админ для изображений товаров
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_main')
    list_editable = ('is_main',)
    list_filter = ('product', 'is_main')
    search_fields = ('product__name',)
    
    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
    image_preview.short_description = "Изображение"

# Регистрация моделей
admin.site.register(Category, CategoryAdmin)