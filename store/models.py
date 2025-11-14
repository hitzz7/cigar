from django.db import models

# Create your models here.
class Category(models.Model):
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    

    def __str__(self):
        return self.name

    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.RESTRICT,related_name='product')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    features = models.TextField()   
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True) 
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255,blank=True, null=True)
    stock = models.PositiveIntegerField(default=0) 
   
    on_sale = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=50)  # e.g. "Single", "Packet of 10"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"{self.product.title} - {self.name}"

class City(models.Model):
    name = models.CharField(max_length=100)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name    
    
class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    landmark = models.TextField(default='', blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} (x{self.quantity})"
    
    