import pytest
from app import app, load_users, save_users
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the Club Management API"}

def test_register(client):
    response = client.post('/register', json={
        "username": "testuser",
        "password": "testpassword",
        "role": "user"
    })
    assert response.status_code == 201
    assert response.json == {"message": "Registered successfully"}

def test_register_existing_user(client):
    client.post('/register', json={
        "username": "testuser",
        "password": "testpassword",
        "role": "user"
    })
    response = client.post('/register', json={
        "username": "testuser",
        "password": "testpassword",
        "role": "user"
    })
    assert response.status_code == 400
    assert response.json == {"error": "Account already exists"}

def test_login(client):
    client.post('/register', json={
        "username": "testuser",
        "password": "testpassword",
        "role": "user"
    })
    response = client.post('/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "token" in response.json

def test_login_invalid_credentials(client):
    response = client.post('/login', json={
        "username": "invaliduser",
        "password": "invalidpassword"
    })
    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}

def test_get_persons_unauthorized(client):
    response = client.get('/persons')
    assert response.status_code == 401
    assert response.json == {"error": "Missing token"}

def test_create_person(client):
    response = client.post('/persons', json={
        "person_name": "John Doe",
        "person_address": "123 Main St",
        "phone_number": "1234567890",
        "email_address": "john@example.com"
    })
    assert response.status_code == 201
    assert response.json == {"message": "Person created successfully"}

def test_create_person_missing_field(client):
    response = client.post('/persons', json={
        "person_name": "John Doe",
        "phone_number": "1234567890"
    })
    assert response.status_code == 400
    assert "error" in response.json

def test_update_person_not_found(client):
    response = client.put('/persons/999', json={
        "person_name": "John Doe Updated"
    })
    assert response.status_code == 404
    assert response.json == {"error": "Person not found"}

def test_delete_person_unauthorized(client):
    response = client.delete('/persons/1')
    assert response.status_code == 403
    assert response.json == {"error": "Access forbidden: insufficient permissions"}

def test_get_clubs(client):
    response = client.get('/clubs')
    assert response.status_code == 200

def test_create_club(client):
    response = client.post('/clubs', json={
        "club_short_name": "Chess Club",
        "club_long_name": "The Chess Club",
        "club_fees": 50,
        "club_description": "A club for chess enthusiasts"
    })
    assert response.status_code == 201
    assert response.json == {"message": "Club created successfully"}

def test_update_club_not_found(client):
    response = client.put('/clubs/999', json={
        "club_short_name": "Updated Club"
    })
    assert response.status_code == 404
    assert response.json == {"error": "Club not found"}

def test_delete_club_unauthorized(client):
    response = client.delete('/clubs/1')
    assert response.status_code == 403
    assert response.json == {"error": "Access forbidden: insufficient permissions"}

def test_get_facilities(client):
    response = client.get('/facilities')
    assert response.status_code == 200

def test_create_facility(client):
    response = client.post('/facilities', json={
        "club_id": 1,
        "facility_name": "Tennis Court",
        "date_available": "2023-01-01",
        "date_not_available": "2023-12-31",
        "facility_cost": 100
    })
    assert response.status_code == 201
    assert response.json == {"message": "Facility created successfully"}

def test_update_facility_not_found(client):
    response = client.put('/facilities/999', json={
        "facility_name": "Updated Facility"
    })
    assert response.status_code == 404
    assert response.json == {"error": "Facility not found"}

def test_delete_facility_unauthorized(client):
    response = client.delete('/facilities/1')
    assert response.status_code == 403
    assert response.json == {"error": "Access forbidden: insufficient permissions"}
    