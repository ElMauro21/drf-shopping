from django.contrib.auth.models import User
from rest_framework import serializers
from shopping_list.models import ShoppingItem, ShoppingList

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username"
        ]

class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingItem
        fields = [
            "id",
            "name",
            "purchased",
            "shopping_list"
        ]
        read_only_fields = ('id', "shopping_list")

    def create(self, validated_data, **kwargs):
        validated_data["shopping_list_id"] = self.context["request"].parser_context[
            "kwargs"
        ]["pk"]
        if ShoppingList.objects.get(
            id=self.context["request"].parser_context["kwargs"]["pk"]
        ).shopping_items.filter(name=validated_data["name"], purchased=False):
            raise serializers.ValidationError("There's already this item on the list")
        return super().create(validated_data)

class ShoppingListSerializer(serializers.ModelSerializer):
    unpurchased_items = serializers.SerializerMethodField()
    members = UserSerializer(many=True, read_only=True)
    class Meta:
        model = ShoppingList
        fields = [
            "id",
            "name",
            "unpurchased_items",
            "members",
        ]
    def get_unpurchased_items(self, obj):
        return [{"name":shopping_item.name} for shopping_item in obj.shopping_items.filter(purchased=False)][:3]