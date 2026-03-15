from rest_framework.routers import DefaultRouter
from shopping_list.api.viewsets import ShoppingItemViewset
from django.urls import path, include

router = DefaultRouter()

router.register('shopping-items',ShoppingItemViewset,basename='shopping-items')

urlpatterns = [
    path("api/",include(router.urls))
]
