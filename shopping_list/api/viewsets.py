from rest_framework.viewsets import ModelViewSet

from shopping_list.api.serializers import ShoppingItemSerializer
from shopping_list.models import ShoppingItem

class ShoppingItemViewset(ModelViewSet):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer