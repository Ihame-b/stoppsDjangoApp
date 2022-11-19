from django.contrib import admin
from .models import *


admin.site.register(
    [Admin, Customer, ProductOwner, LinfoxUser, Cargo, Category, Product, Cart, CartProduct, Order, ProductImage])
