import os
import time
import shutil

from fastapi.testclient import TestClient
from src.main import app


def login_user(
        client: TestClient, credentials: dict = {"username": "test_user", "password": "test_password"}, 
        register_route: str = "/auth/register", login_route: str = "/auth/login"
        ) -> str:
    client.post(register_route, data = credentials)
    response = client.post(login_route, data = credentials)
    return response.json()["access_token"]


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


class TestProjectsAPI:

    def setup_class(self):
        tests_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        scripts_dir = os.path.join(tests_dir, "scripts")

        self.users_dir = os.path.join(tests_dir, "users")
        self.project_script = os.path.join(scripts_dir, "demo_app.py")

    def teardown_method(self):
        for item in os.listdir(self.users_dir):
            path = os.path.join(self.users_dir, item)
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors = True)

    def test_unauthorized(self):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            response = client.post(
                "/test_user", 
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )
            assert response.status_code == 401
            assert response.json() == {
                "detail": "Not authenticated"
            }

    def test_insufficient_permissions(self):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            access_token = login_user(client)
            response = client.post(
                "/test_user_insufficient_permissions",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )
            assert response.status_code == 401
            assert response.json() == {
                "detail": "Insufficient permissions."
            }

    def test_create_new_project(self, monkeypatch_root, monkeypatch_users_dir):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            access_token = login_user(client)
            response = client.post(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )
            assert response.status_code == 200
            assert response.json() == {
                "name": "test_project",
                "owner": {
                    "username": "test_user"
                }
            }

            user_dir = os.path.join(self.users_dir, "test_user")
            project_dir = os.path.join(user_dir, "test_project")
            project_script = os.path.join(project_dir, "app.py")

            assert os.path.isdir(user_dir)
            assert os.path.isdir(project_dir)
            assert os.path.isfile(project_script)

            response = client.get("/test_user/test_project/")
            assert response.status_code == 200
            assert response.json() == "index!"

    def test_create_existing_project(self, monkeypatch_root, monkeypatch_users_dir):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            access_token = login_user(client)
            client.post(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )

            response = client.post(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )
            assert response.status_code == 409
            assert response.json() == {"detail": "Project already exists."}

    def test_read_projects(self):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            access_token = login_user(client)
            client.post(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )
            response = client.get(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
            )
            assert response.status_code == 200
            assert response.json() == [{
                "name": "test_project",
                "owner": {
                    "username": "test_user"
                }
            }]

    def test_update_non_existing_project(self, monkeypatch_root, monkeypatch_users_dir):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            access_token = login_user(client)
            response = client.put(
                "/test_user/test_project",
                headers = {"Authorization": f"Bearer {access_token}"},
                files = {"project_script": f},
            )
            assert response.status_code == 404
            assert response.json() == {
                "detail": "Project does not exist."
            }

    def test_update_existing_project(self, monkeypatch_root, monkeypatch_users_dir):
        with TestClient(app) as client, open(self.project_script, "rb") as f:
            access_token = login_user(client)
            response = client.post(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )

            response = client.put(
                "/test_user/test_project",
                headers = {"Authorization": f"Bearer {access_token}"},
                files = {"project_script": f},
            )
            assert response.status_code == 200
            assert response.json() == {
                "name": "test_project",
                "owner": {
                    "username": "test_user"
                }
            }

    def test_delete_project(self, monkeypatch_root, monkeypatch_users_dir):
        with TestClient(app) as client, \
            open(self.project_script, "rb") as f:

            access_token = login_user(client)
            response = client.post(
                "/test_user",
                headers = {"Authorization": f"Bearer {access_token}"},
                data = {"project_name": "test_project"},
                files = {"project_script": f},
            )

            response = client.delete(
                "/test_user/test_project",
                headers = {"Authorization": f"Bearer {access_token}"},
            )
            assert response.status_code == 200
            assert response.json() == []