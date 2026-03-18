from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from shopping_list.api.serializers import ShoppingItemSerializer
from shopping_list.models import ShoppingItem

class ShoppingItemViewset(ModelViewSet):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer

    @action(detail=False, methods=['DELETE'], url_path='delete-all-purchased', url_name='delete_all_purchased')
    def delet_purchased(self,request):
        ShoppingItem.objects.filter(purchased=True).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['PATCH'], url_path='mark-bulk-purchased', url_name='mark_bulk_purchased')
    def mark_bulk_purchased(self, request):
        try: 
            queryset = ShoppingItem.objects.filter(id__in=request.data['shopping_items'])
            queryset.update(purchased=True)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)