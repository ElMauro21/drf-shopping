import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from shopping_list.models import ShoppingList, ShoppingItem

## Shopping lists tests

def test_valid_shopping_list_is_created(db):
    url = reverse("all_shopping_lists")
    client = APIClient()
    data = {
        "name": "Groceries"
    }
    response = client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Groceries"
    assert ShoppingList.objects.count() == 1
    assert str(ShoppingList.objects.get()) == "Groceries"

def test_shopping_list_name_missing_returns_bad_request(db):
    client = APIClient()
    url = reverse("all_shopping_lists")
    data = {
        "something_else": "blahblah"
    }
    response = client.post(path=url,data=data,format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_delete_single_shopping_list(db):
    url = reverse("all_shopping_lists")
    client = APIClient()
    data = {
        "name": "Groceries"
    }
    client.post(path=url, data=data, format="json")
    obj = ShoppingList.objects.get()

    url_delete = reverse("shopping_list_detail",kwargs={"pk": obj.id})
    response = client.delete(path=url_delete)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ShoppingList.objects.count() == 0

def test_all_shopping_lists_are_listed(db):
    url = reverse("all_shopping_lists")
    client = APIClient()
    ShoppingList.objects.create(name="Groceries")
    ShoppingList.objects.create(name="Technology")
    response = client.get(url, format="json")

    assert len(response.data) == 2 
    assert response.data[0]["name"] == "Groceries"
    assert response.data[1]["name"] == "Technology"

def test_shopping_list_is_retrieve_by_id(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail",args=[shopping_list.id])
    client = APIClient()
    response = client.get(path=url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"

def test_shopping_list_includes_only_corresponding_items(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    another_shopping_list = ShoppingList.objects.create(name="Books")
    ShoppingItem.objects.create(shopping_list=shopping_list, name="Eggs", purchased=False)
    ShoppingItem.objects.create(shopping_list=another_shopping_list, name="The seven sisters", purchased=False)

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.get(url, format="json")

    assert len(response.data["shopping_items"]) == 1
    assert response.data["shopping_items"][0]["name"] == "Eggs"

def test_shopping_list_name_is_changed(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.put(path=url,data={"name": "Technology"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Technology"

def test_shopping_list_not_changed_because_name_missing(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.put(path=url,data={"Another_name": "New_name"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_shopping_list_name_is_changed_with_partial_update(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.patch(path=url,data={"name": "Technology"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Technology"

def test_partial_update_with_missing_name_has_no_impact(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    client = APIClient()
    response = client.patch(path=url,data={"Another_name": "Technology"}, format="json")

    assert response.status_code == status.HTTP_200_OK

## Shoping items tests 

def test_valid_shopping_item_is_created(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("add_shopping_item", args=[shopping_list.id])

    data = {
        "name": "milk",
        "purchased": False,
    }
    client = APIClient()
    response = client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert str(ShoppingItem.objects.get()) == "milk"

def test_create_shopping_item_missing_data_returns_bad_request(db):
    shopping_list = ShoppingList.objects.create(name="Groceries")
    url = reverse("add_shopping_item", args=[shopping_list.id])

    data = {
        "name": "milk"
    }

    client = APIClient()
    response = client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_shopping_item_is_retrieve_by_id(db, create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"

def test_change_shopping_item_purchased_status(db, create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")

    url = reverse("shopping_item_detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()

    data = {
        "name": "Chocolate",
        "purchased": True
    }

    response = client.put(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True

def test_change_shopping_item_purchased_status_with_missing_data_return_bad_request(db, create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    
    data = {"purchased": True}
    respose = client.put(path=url, data=data, format="json")

    assert respose.status_code == status.HTTP_400_BAD_REQUEST

def test_change_shopping_item_purchased_status_with_partial_update(db, create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    client = APIClient()
    
    data = {"purchased": True}
    respose = client.patch(path=url, data=data, format="json")

    assert respose.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True

def test_shopping_item_is_deleted(db,create_shopping_item):
    shopping_item = create_shopping_item(name="Chocolate")

    url = reverse("shopping_item_detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    client = APIClient()
    response = client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ShoppingItem.objects.count() == 0