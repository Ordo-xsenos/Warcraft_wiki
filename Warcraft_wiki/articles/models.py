from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
import stripe
from django.conf import settings
User = get_user_model()


class Article(models.Model):
    title = models.CharField(max_length=70, unique=True)
    content = models.TextField()
    quote = models.CharField(max_length=9999, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления

    #sub_category = models.ManyToManyField(Subcategory)
    def __str__(self):
        return self.title


class Fotochki:
    article = models.ForeignKey("Article", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидание оплаты'),
        ('paid', 'Оплачено'),
        ('canceled', 'Отменено')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Article, through='OrderItem')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)

    def str(self):
        return f'Заказ {self.id} | Пользователь: {self.user.username} | Статус: {self.get_status_display()}'

    def get_checkout_session(self):
        line_items = []

        for item in self.orderitem_set.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.product_name,
                    },
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=settings.SITE_URL + reverse('products:payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.SITE_URL + reverse('products:payment_cancel'),
        )

        self.session_id = session.id
        self.save()
        return session.id

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def str(self):
      return f'{self.product.Article_name} x {self.quantity}'

class PaidOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paid_orders")
    product = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, unique=True)

    def str(self):
        return f"Оплаченный заказ {self.id} | {self.user.username} | {self.product.product_name}"