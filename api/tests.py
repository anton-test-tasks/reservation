from django.test import TestCase
import pytest
import requests
import json

base_url = 'http://127.0.0.1:8000/'
register_user_url = 'api/user/register/'
user_login_url = 'token-auth'
user_profile_url = 'api/user/'
meeting_rooms_url = 'api/meeting_room/'
reservations_url = 'api/reservation/'

user_data = {"username": "test_user", "password": "test_password", "email": "test_user@mail.com",
             "first_name": "test_user_first_name", "last_name": "test_user_last_name"}
updated_user_data = {"first_name": "updated_first_name", "last_name": "updated_last_name"}
user_login_data = {"username": "test_user", "password": "test_password"}
meeting_room_data = {"name": "t_meeting_room", "amount_people": 10}
reservation_data = {"title": "test_reservation_title", "meeting_room": 1, "start_date_time": "2021-07-06T22:00:44Z",
                    "end_date_time": "2021-07-06T22:30:47Z", "employees": [1, 2]}
auth_token = ''
user_id = ''
meeting_room_id = ''
reservation_id = ''


def test_register_user():
    response = requests.post(url=base_url + register_user_url, json=user_data)
    assert str(response) == '<Response [201]>'


def test_login_user():
    response = requests.post(url=base_url + user_login_url, json=user_login_data)
    global auth_token
    auth_token = response.json()["token"]
    assert str(response) == '<Response [200]>'


def test_get_user_profile():
    response = requests.get(url=base_url + user_profile_url, headers={"Authorization": "token " + auth_token})
    global user_id
    user_id = response.json()[0]["id"]
    assert str(response) == '<Response [200]>'
    assert response.json()[0]["username"] == user_data["username"]


def test_update_user_profile():
    update_response = requests.patch(url=base_url + user_profile_url + str(user_id) + "/",
                                     headers={"Authorization": "token " + auth_token}, json=updated_user_data)
    assert str(update_response) == '<Response [200]>'
    get_response = requests.get(url=base_url + user_profile_url, headers={"Authorization": "token " + auth_token})
    assert str(get_response) == '<Response [200]>'
    assert get_response.json()[0]["first_name"] == updated_user_data["first_name"]
    assert get_response.json()[0]["last_name"] == updated_user_data["last_name"]


def test_create_meeting_room():
    response = requests.post(url=base_url + meeting_rooms_url, json=meeting_room_data,
                             headers={"Authorization": "token " + auth_token})
    global meeting_room_id
    print(response.json())
    meeting_room_id = response.json()['id']
    assert str(response) == '<Response [200]>'


def test_get_meeting_room():
    response = requests.get(url=base_url + meeting_rooms_url + str(meeting_room_id) + "/",
                            headers={"Authorization": "token " + auth_token})
    assert str(response) == '<Response [200]>'
    assert response.json()["name"] == meeting_room_data["name"]


def test_update_meeting_room():
    response = requests.patch(url=base_url + meeting_rooms_url + str(meeting_room_id) + "/",
                              json={"name": "up_m_room"},
                              headers={"Authorization": "token " + auth_token})
    print(response.json())
    assert str(response) == '<Response [200]>'
    get_response = requests.get(url=base_url + meeting_rooms_url + str(meeting_room_id) + "/",
                                headers={"Authorization": "token " + auth_token})
    assert str(get_response) == '<Response [200]>'
    assert get_response.json()["name"] == "up_m_room"


def test_create_reservation():
    reservation_data["meeting_room"] = meeting_room_id
    reservation_data["employees"] = [user_id,]
    response = requests.post(url=base_url + reservations_url, json=reservation_data,
                             headers={"Authorization": "token " + auth_token})
    global reservation_id
    reservation_id = response.json()['id']
    assert str(response) == '<Response [201]>'


def test_update_reservation():
    response = requests.patch(url=base_url + reservations_url + str(reservation_id) + "/",
                              json={"title": "test_updated_reservation", "meeting_room": meeting_room_id,
                                    "start_date_time": "2021-07-06T22:00:44Z",
                                    "end_date_time": "2021-07-06T22:30:47Z"},
                              headers={"Authorization": "token " + auth_token})
    assert str(response) == '<Response [200]>'
    get_response = requests.get(url=base_url + reservations_url + str(reservation_id) + "/",
                                headers={"Authorization": "token " + auth_token})
    assert str(get_response) == '<Response [200]>'
    assert get_response.json()["title"] == "test_updated_reservation"


def test_delete_reservation():
    response = requests.delete(url=base_url + reservations_url + str(reservation_id) + "/",
                               headers={"Authorization": "token " + auth_token})
    assert str(response) == '<Response [204]>'
    get_response = requests.get(url=base_url + reservations_url + str(reservation_id) + "/",
                                headers={"Authorization": "token " + auth_token})
    assert str(get_response) == '<Response [404]>'
