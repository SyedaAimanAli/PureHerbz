from django.contrib import admin
from .models import Customer, Orders, Product, Review

# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     class Media:
#         js= ('tinyInject.js',)
        
# admin.site.register(Wishlist)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'sno')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'created_at')
    list_filter = ['created_at']

admin.site.register(Customer)
admin.site.register(Orders)
# admin.site.register(Product)