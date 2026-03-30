from rest_framework import generics
from shopping_list.api.serializers import ShoppingListSerializer, ShoppingItemSerializer
from shopping_list.models import ShoppingList, ShoppingItem
from shopping_list.api.permissions import (
    AllShoppingItemsShoppingListMembersOnly,
    ShoppingItemShoppingListMembersOnly,
    ShoppingListMembersOnly,
)
from shopping_list.api.pagination import LargerResultsSetPagination

# Create your views here.

class ListAddShoppingList(generics.ListCreateAPIView):
    serializer_class = ShoppingListSerializer

    def perform_create(self, serializer):
        shopping_list = serializer.save()
        shopping_list.members.add(self.request.user)
        return shopping_list
    
    def get_queryset(self):
        return ShoppingList.objects.filter(members=self.request.user).order_by("-last_interaction")
    

class ShoppingListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = [ShoppingListMembersOnly]

class ShoppingItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer
    permission_classes = [ShoppingItemShoppingListMembersOnly]
    lookup_url_kwarg = 'item_pk'

class ListAddShoppingItem(generics.ListCreateAPIView):
    serializer_class = ShoppingItemSerializer
    permission_classes = [AllShoppingItemsShoppingListMembersOnly]
    pagination_class = [LargerResultsSetPagination]

    def perform_create(self, serializer):
        list_uuid = self.kwargs.get("pk")
        serializer.save(shopping_list_id=list_uuid)

    def get_queryset(self):
        shopping_list = self.kwargs["pk"]
        queryset = self.queryset = ShoppingItem.objects.filter(shopping_list=shopping_list).order_by("purchased")
        return queryset