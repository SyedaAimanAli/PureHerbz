from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField 
from django.contrib.auth.models import AbstractUser

class Customer(AbstractUser): 
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  
    address = models.CharField(max_length=255, null=True, blank=True)  
    mobile = models.CharField(max_length=20, null=False)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# Product Model
class Product(models.Model): 
    name = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to='media/images/', null=True, blank=True)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    sno = models.IntegerField(unique=True) 
    category = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Rating between 1 and 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.email} for {self.product.name}"

# # Wishlist Model
# class Wishlist(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('user', 'product')  # Prevent duplicate wishlist entries

#     def __str__(self):
#         return f"{self.user.username} - {self.product.name}"


# Orders Model
class Orders(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
    )
    id = models.IntegerField(unique=True, primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    total_price = models.FloatField(max_length=20, default=0)
    products = models.JSONField(default=dict) 
    zipcode = models.PositiveIntegerField()

    def __str__(self):
        return f"Order by {self.customer.email} on {self.order_date}"


# class OrderProduct(models.Model):
#     order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} in {self.order}"



# # Feedback Model
# class Feedback(models.Model):
#     name = models.CharField(max_length=255)
#     feedback = models.TextField()  # Changed to TextField for longer feedback
#     date = models.DateField(auto_now_add=True, null=True)

#     def __str__(self):
#         return self.name
