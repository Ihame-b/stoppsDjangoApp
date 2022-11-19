from tokenize import String
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="admins")
    mobile = models.CharField(max_length=20)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(verbose_name="Address",max_length=100, null=True, blank=True, default="kk 310st")
    town = models.CharField(verbose_name="Town/City",max_length=100, null=True, blank=True, default="kigali")
    county = models.CharField(verbose_name="County",max_length=100, null=True, blank=True, default="Rwanda")
    post_code = models.CharField(verbose_name="Post Code",max_length=8, null=True, blank=True, default="00000")
    has_profile = models.BooleanField(default = False)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.user.username
    def __str__(self):
        return f'{self.user}'

class LinfoxUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="linfox")
    mobile = models.CharField(max_length=20)
    

    def __str__(self):
        return self.user.username   

class ProductOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="productowner")
    mobile = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username              


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    joined_on = models.DateTimeField(auto_now_add=True)
    address = models.CharField(verbose_name="Address",max_length=100, null=True, blank=True, default="kk 310st")
    town = models.CharField(verbose_name="Town/City",max_length=100, null=True, blank=True, default="kigali")
    county = models.CharField(verbose_name="County",max_length=100, null=True, blank=True, default="Rwanda")
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.full_name


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    address = models.CharField(verbose_name="Address",max_length=100, null=True, blank=True, default="kk 330st")
    town = models.CharField(verbose_name="Town/City",max_length=100, null=True, blank=True, default="kigali")
    county = models.CharField(verbose_name="County",max_length=100, null=True, blank=True, default="Rwanda")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products")
    marked_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField()
    description = models.TextField()
    warranty = models.CharField(max_length=300, null=True, blank=True)
    return_policy = models.CharField(max_length=300, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    productowner=models.CharField(User.get_full_name, max_length=300)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return self.product.title

class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)   
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return "Cart: " + str(self.id)


Company = (
    ("LINFOX", "linfox"),
    ("KBS", "kbs"),
    ("OTHERS", "others"),
)
CARGO_STATUS = (
    ("Cargo Available", "Cargo Available"),
    ("Cargo Not Available", "Cargo Not Available"),
  
)

class Cargo(models.Model):
        CampanyName = models.CharField(max_length=20, choices=Company, default="Linfox")
        driverName=models.CharField(max_length=20, default="bob")
        # driverphone=models.CharField(max_length=20, default="0788558866")
        #driverEmail=models.EmailField(default="ihamegrbt@gmail.com")
        joined_on = models.DateTimeField(auto_now_add=True)
        address = models.CharField(verbose_name="Address",max_length=100, null=True, blank=True, default="kk 310st")
        image = models.ImageField(upload_to="products", default=0)
        price = models.PositiveIntegerField(default=0)
        view_count = models.PositiveIntegerField(default=0)
        cargo_status = models.CharField(max_length=50, choices=CARGO_STATUS, default="Cargo Available")

  
        def __str__(self):
            return "Cardo: " + str(self.id)     

class LinfoxImage(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")
    

    def __str__(self):
        return self.cargo.CampanyName              


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE,blank=True,null=True, default=Cargo.objects.first().pk )
    # driver= models.ForeignKey(Cargo.driverName,max_length=300,on_delete=models.CASCADE, default=Cargo.objects.first().pk)

    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)



METHOD = (
    ("Cash On Delivery", "Cash On Delivery"),
    ("MOMO", "momo"),
    ("Khalti", "Khalti"),
    ("Esewa", "Esewa"),
    
)


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Cash On Delivery")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)

    def __str__(self):
        return "Order: " + str(self.id)
