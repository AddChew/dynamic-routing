from fastapi.testclient import TestClient
from src.main import app


class TestAuthAPI:
    
    def setup_class(self):
        prefix = "/auth"
        self.register_route = f"{prefix}/register"
        self.login_route = f"{prefix}/login"

    def test_register_new_user(self):
        with TestClient(app) as client:
            response = client.post(
                self.register_route, 
                data = {
                    "username": "test_user",
                    "password": "test_password"
            })
            assert response.status_code == 200
            assert response.json() == {
                "username": "test_user",
                "projects": []
            }

    def test_register_existing_user(self):
        with TestClient(app) as client:
            client.post(
                self.register_route, 
                data = {
                    "username": "test_existing_user",
                    "password": "test_existing_password",
            })

            response = client.post(
                self.register_route, 
                data = {
                    "username": "test_existing_user",
                    "password": "test_existing_password",
            })
            assert response.status_code == 409
            assert response.json() == {
                "detail": "User already exists."
            }

    def test_login_invalid_username(self):
        with TestClient(app) as client:
            response = client.post(
                self.login_route, 
                data = {
                    "username": "test_invalid_user",
                    "password": "test_password",
            })
            assert response.status_code == 401
            assert response.json() == {
                "detail": "Incorrect username or password."
            }

    def test_login_invalid_password(self):
        with TestClient(app) as client:
            client.post(
                self.register_route, 
                data = {
                    "username": "test_user",
                    "password": "test_invalid_password",
            })

            response = client.post(
                self.login_route, 
                data = {
                    "username": "test_user",
                    "password": "test_password",
            })
            assert response.status_code == 401
            assert response.json() == {
                "detail": "Incorrect username or password."
            }

    def test_login_valid_user(self):
        with TestClient(app) as client:
            client.post(
                self.register_route, 
                data = {
                    "username": "test_valid_user",
                    "password": "test_valid_password",
            })

            response = client.post(
                self.login_route, 
                data = {
                    "username": "test_valid_user",
                    "password": "test_valid_password",
            })
            assert response.status_code == 200

            json_response = response.json()
            assert json_response["token_type"] == "bearer"
            assert "access_token" in json_response