# admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage,ProductVariant
from .models import City, Order, OrderItem
# Define an inline class for ProjectImage
class ProductImageInline(admin.TabularInline):  # You can use StackedInline for a different layout
    model = ProductImage
    extra = 1  # Number of empty forms to display in the admin
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'price')  # what to show in inline
    show_change_link = True

# Customize the Project admin
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline,ProductVariantInline] 
    # Include the ProjectImage inline in the Project admin

# Customize the Project admin

# Register your models
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)  
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # do not show extra empty rows
    readonly_fields = ('title', 'price', 'quantity', 'image_url')  # prevent editing if you want
    can_delete = False

# Admin for Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'city', 'total_price', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'city', 'created_at')
    search_fields = ('name', 'email', 'phone', 'address')
    readonly_fields = ('total_price', 'created_at')
    inlines = [OrderItemInline]

# Admin for City
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_charge')
    search_fields = ('name',)
