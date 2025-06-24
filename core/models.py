# models.py
from django.db import models
from django.urls import reverse
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская категория"
    )
    slug = models.SlugField(unique=True)
    
    
    def get_descendants(self, include_self=False):
        descendants = []
        if include_self:
            descendants.append(self)
        for child in self.children.all():
            descendants += child.get_descendants(include_self=True)
        return descendants
    
    
    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})
    
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        
        
    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    categories = models.ManyToManyField(Category)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    skidka_price = models.DecimalField(max_digits=10, blank=True, null=True, decimal_places=2,verbose_name="цена со скидкой")
    
    stock = models.PositiveIntegerField()
    is_top = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    barcode = models.CharField(max_length=50, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def __str__(self):
        return f" #{self.id} - {self.name}"
   
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
    
    
class ProductSpecification(models.Model):
    """
    Модель для хранения названий характеристик (например, "Вес", "Цвет")
    """
    name = models.CharField(max_length=100, verbose_name="Название характеристики")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Идентификатор")
    
    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductSpecificationValue(models.Model):
    """
    Модель для хранения значений характеристик конкретного товара
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='specifications',
        verbose_name="Товар"
    )
    specification = models.ForeignKey(
        ProductSpecification, 
        on_delete=models.CASCADE, 
        related_name='values',
        verbose_name="Характеристика"
    )
    value = models.CharField(max_length=255, verbose_name="Значение")
    
    class Meta:
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значения характеристик"
        ordering = ['specification__name']
        unique_together = ('product', 'specification')
    
    def __str__(self):
        return f"{self.specification.name}: {self.value}"
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_main = models.BooleanField(default=False)  # Добавьте это поле

    class Meta:
        verbose_name = "Изображение продукта"
        verbose_name_plural = "Изображении продуктов"
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    comments = models.TextField(blank=True, verbose_name="Комментарий")
    
    # Информация о заказе
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                           null=True, blank=True)
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f" #{self.id} - {self.full_name}"
   
    
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Заказ #{self.product} - {self.order}"
    
    class Meta:
        verbose_name = "Элементы заказа"
        verbose_name_plural = "Элементы заказов"
        
    
class KaruselImage(models.Model):
    title = models.CharField(max_length=20,)
    image = models.ImageField(upload_to='karusel_products/')
    is_main = models.BooleanField(default=False)  # Добавьте это поле
    url = models.URLField(verbose_name='Сылка',blank=True,null=True,)
    
    def __str__(self):
        return f"Картинка #{self.id} - {self.title}"
    
    class Meta:
        verbose_name = "Фотка Карусели"
        verbose_name_plural = "Фотки Карусели"

# core/models.py
class EmailRecipient(models.Model):
    purpose = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"{self.purpose}: {self.email}"
    
    class Meta:
        verbose_name = "Gmail Рассылка"
        verbose_name_plural = "Gmail Рассылки"

class Letter(models.Model):
    name = models.CharField(max_length=100,verbose_name='фио')
    number_phone = models.CharField(max_length=12,verbose_name='телефон')
    pochta = models.EmailField(verbose_name='почта') 
    cat = models.CharField(max_length=900 ,verbose_name='сообщение')   
    
    def __str__(self):
        return f"{self.name}: {self.pochta}"
    
    class Meta:
        verbose_name = "Письмо Менеджеру"
        verbose_name_plural = "Письма Менеджерам"

class Cart(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.session_key}"
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        price = self.product.skidka_price if self.product.skidka_price else self.product.price
        return price * self.quantity


# models.py
from django.db import models

class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.username or self.first_name or self.chat_id
    
    class Meta:
        verbose_name = "Телеграм пользовател"
        verbose_name_plural = "Телеграм пользователи"
        