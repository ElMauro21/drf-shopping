from django.contrib import admin
from shopping_list.models import ShoppingItem, ShoppingList

# Register your models here.

admin.site.register(ShoppingItem)
admin.site.register(ShoppingList)