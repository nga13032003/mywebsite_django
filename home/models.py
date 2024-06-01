from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Post (models.Model):
    title = models.CharField(max_length= 100)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sanpham = models.ForeignKey('home.SanPham', on_delete=models.CASCADE, related_name='comments')
    timestamp = models.DateTimeField(default=timezone.now)
    body = models.TextField()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.sanpham.TenSP}'

class Loai(models.Model):
    TenLoai = models.CharField(max_length=100)

    def __str__(self):
        return self.TenLoai
class SanPham(models.Model):
    id = models.AutoField(primary_key=True)
    TenSP = models.CharField(max_length=100)
    DonGia = models.DecimalField(max_digits=10, decimal_places=2)
    HinhAnh = models.CharField(max_length=255)
    MoTa = models.TextField()
    MaLoai = models.ForeignKey('Loai', on_delete=models.CASCADE)
    SoLuong = models.PositiveIntegerField(default=0)  # Thêm trường SoLuong
    buyers = models.ManyToManyField(User, related_name='purchased_products')
    khuyen_mai = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.TenSP
    def average_rating(self):
        sum_ratings = sum([rating.rating for rating in self.ratings.all()])
        if self.ratings.count() > 0:
            return sum_ratings / self.ratings.count()
        return 0
class CartItem(models.Model):
    quantity = models.PositiveIntegerField(default=1)
    sanpham = models.ForeignKey('home.SanPham', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def subtotal(self):
        return self.sanpham.DonGia * self.quantity

    class Meta:
        db_table = 'home_cartitem'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Các trường mới
    shipping_address = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Pending')  # Trạng thái mặc định là Pending
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def calculate_total_amount(self):
        order_items = self.order_items.all()
        total = sum(item.total for item in order_items)
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    sanpham = models.ForeignKey('home.SanPham', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.price = self.sanpham.DonGia
        self.total = self.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.sanpham.TenSP} for {self.order}"
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.message}'
    
class DanhGia(models.Model):
    sanpham = models.ForeignKey(SanPham, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['sanpham', 'user']]