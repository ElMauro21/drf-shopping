import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

from shopping_list.models import ShoppingList, ShoppingItem

## Shopping lists tests

def test_valid_shopping_list_is_created(db, create_authenticated_client,create_user):
    url = reverse("all_shopping_lists")
    client = create_authenticated_client(create_user())
    data = {
        "name": "Groceries"
    }
    response = client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Groceries"
    assert ShoppingList.objects.count() == 1
    assert str(ShoppingList.objects.get()) == "Groceries"

def test_shopping_list_name_missing_returns_bad_request(db, create_authenticated_client, create_user):
    user = create_user()
    client = create_authenticated_client(user)
    url = reverse("all_shopping_lists")
    data = {
        "something_else": "blahblah"
    }
    response = client.post(path=url,data=data,format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_delete_single_shopping_list(db, create_authenticated_client, create_user, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ShoppingList.objects.count() == 0

def test_client_retrieves_only_shopping_lists_they_are_member_of(db, create_authenticated_client, create_user, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    url = reverse("all_shopping_lists")
    create_shopping_list(user, name="Groceries")
    another_user = User.objects.create_user("test_user","test@example.com","testpassword")
    create_shopping_list(another_user, name="Technology")
    response = client.get(url, format="json")

    assert len(response.data) == 1
    assert response.data[0]["name"] == "Groceries"

def test_shopping_list_is_retrieve_by_id(db, create_authenticated_client, create_user, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user=user)
    url = reverse("shopping_list_detail",args=[shopping_list.id])
    response = client.get(path=url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"

def test_shopping_list_includes_only_corresponding_items(db, create_user, create_authenticated_client, create_shopping_list, create_shopping_item):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    another_shopping_list = create_shopping_list(user, name="Books")
    ShoppingItem.objects.create(shopping_list=shopping_list, name="Eggs", purchased=False)
    ShoppingItem.objects.create(shopping_list=another_shopping_list, name="The seven sisters", purchased=False)

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.get(url, format="json")

    assert len(response.data["shopping_items"]) == 1
    assert response.data["shopping_items"][0]["name"] == "Eggs"

def test_shopping_list_name_is_changed(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("shopping_list_detail", args=[shopping_list.id]) 
    response = client.put(path=url,data={"name": "Technology"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Technology"

def test_shopping_list_not_changed_because_name_missing(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.put(path=url,data={"Another_name": "New_name"}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_shopping_list_name_is_changed_with_partial_update(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.patch(path=url,data={"name": "Technology"}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Technology"

def test_partial_update_with_missing_name_has_no_impact(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("shopping_list_detail", args=[shopping_list.id])
    response = client.patch(path=url,data={"Another_name": "Technology"}, format="json")

    assert response.status_code == status.HTTP_200_OK

## Shoping items tests 

def test_valid_shopping_item_is_created(db,create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("add_shopping_item", args=[shopping_list.id])

    data = {
        "name": "milk",
        "purchased": False,
    }
    response = client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert str(ShoppingItem.objects.get()) == "milk"

def test_create_shopping_item_missing_data_returns_bad_request(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list(user)
    url = reverse("add_shopping_item", args=[shopping_list.id])

    data = {
        "name": "milk"
    }
    response = client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_shopping_item_is_retrieve_by_id(db, create_user, create_authenticated_client ,create_shopping_item):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"

def test_change_shopping_item_purchased_status(db, create_shopping_item, create_user, create_authenticated_client):
    user = create_user()
    client = create_authenticated_client(user) 
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping_item_detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    data = {
        "name": "Chocolate",
        "purchased": True
    }

    response = client.put(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True

def test_change_shopping_item_purchased_status_with_missing_data_return_bad_request(db, create_shopping_item, create_user, create_authenticated_client):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    
    data = {"purchased": True}
    respose = client.put(path=url, data=data, format="json")

    assert respose.status_code == status.HTTP_400_BAD_REQUEST

def test_change_shopping_item_purchased_status_with_partial_update(db, create_shopping_item, create_user, create_authenticated_client):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})
    
    data = {"purchased": True}
    respose = client.patch(path=url, data=data, format="json")

    assert respose.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True

def test_shopping_item_is_deleted(db,create_shopping_item, create_user, create_authenticated_client):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate",user=user)

    url = reverse("shopping_item_detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ShoppingItem.objects.count() == 0
    
def test_update_shopping_list_restricted_if_not_member(db, create_user, create_authenticated_client,create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_list = create_shopping_list(shopping_list_creator)

    url = reverse("shopping_list_detail", args=[shopping_list.id])
    data = {
        "name": "Food",
    }

    response = client.put(path=url,data=data,format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_partial_update_shopping_list_restricted_if_not_member(db, create_user, create_authenticated_client,create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_list = create_shopping_list(shopping_list_creator)

    url = reverse("shopping_list_detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response = client.patch(path=url,data=data,format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_shopping_list_restricted_if_not_member(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_list = create_shopping_list(shopping_list_creator)

    url = reverse("shopping_list_detail", args=[shopping_list.id])

    response = client.delete(path=url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_can_retrieve_shopping_list(db, create_user, create_shopping_list, admin_client):
    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("shopping_list_detail", args=[shopping_list.id])

    response = admin_client.get(path=url, format="json")

    assert response.status_code == status.HTTP_200_OK

def test_not_member_of_list_can_not_add_shopping_item(db, create_user, create_authenticated_client, create_shopping_list):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_list = create_shopping_list(shopping_list_creator)

    url = reverse("add_shopping_item",args=[shopping_list.id])

    data = {
        "name": "Milk",
        "purchased": False,
    }

    response = client.post(path=url,data=data,format="json")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_can_add_shopping_items(db, create_user, admin_client, create_shopping_list):
    user = create_user()
    shopping_list = create_shopping_list(user)

    url = reverse("add_shopping_item", args=[shopping_list.id])

    data = {
        "name": "Milk",
        "purchased": False,
    }

    response = admin_client.post(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

def test_shopping_item_detail_access_restricted_if_not_member_of_shopping_list(db, create_user,create_authenticated_client, create_shopping_list, create_shopping_item):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_item = create_shopping_item(name="Chocolate", user=shopping_list_creator)

    url = reverse("shopping_item_detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = client.get(path=url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_shopping_item_update_restricted_if_not_member_of_shopping_list(db, create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_cretor = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_item = create_shopping_item(name="Chocolate", user=shopping_list_cretor)

    url = reverse("shopping_item_detail", kwargs={"pk":shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    data = {
        "name": "Chocolate",
        "purchased": True
    }

    response = client.put(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_shopping_item_partial_update_restricted_if_not_member_of_shopping_list(db,create_user, create_authenticated_client,create_shopping_item):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shoppin_item = create_shopping_item(name="Chocolate", user=shopping_list_creator)

    url = reverse("shopping_item_detail", kwargs={"pk": shoppin_item.shopping_list.id, "item_pk": shoppin_item.id})

    data = {
        "purchased": True
    }

    response = client.patch(path=url, data=data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_shopping_item_delete_restricted_if_not_member_of_shopping_list(db, create_user, create_authenticated_client, create_shopping_item):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list_creator = User.objects.create_user("Test_user","test@example.com","testpassword")
    shopping_item = create_shopping_item(name="chocolate", user=shopping_list_creator)

    url = reverse("shopping_item_detail",kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = client.delete(path=url, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_can_retrieve_single_shopping_item(db, create_user, create_shopping_item, admin_client):
    user = create_user()
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse("shopping_item_detail", kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id})

    response = admin_client.get(path=url, format="json")

    assert response.status_code == status.HTTP_200_OK