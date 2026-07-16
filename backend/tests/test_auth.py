"""Auth endpoint tests: register, login, /users/me."""


class TestRegister:
    def test_register_success(self, client):
        response = client.post(
            "/api/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["username"] == "alice"
        assert body["email"] == "alice@example.com"
        # The password must never appear in any form
        assert "password" not in body
        assert "hashed_password" not in body

    def test_register_duplicate_username(self, client):
        payload = {"username": "alice", "email": "alice@example.com", "password": "password123"}
        client.post("/api/auth/register", json=payload)
        response = client.post(
            "/api/auth/register",
            json={"username": "alice", "email": "other@example.com", "password": "password123"},
        )
        assert response.status_code == 409

    def test_register_duplicate_email(self, client):
        client.post(
            "/api/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )
        response = client.post(
            "/api/auth/register",
            json={"username": "bob", "email": "alice@example.com", "password": "password123"},
        )
        assert response.status_code == 409

    def test_register_short_username_rejected(self, client):
        response = client.post(
            "/api/auth/register",
            json={"username": "ab", "email": "ab@example.com", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_short_password_rejected(self, client):
        response = client.post(
            "/api/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "short"},
        )
        assert response.status_code == 422


class TestLogin:
    def _register(self, client):
        client.post(
            "/api/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )

    def test_login_success(self, client):
        self._register(client)
        response = client.post(
            "/api/auth/login", data={"username": "alice", "password": "password123"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"]

    def test_login_wrong_password(self, client):
        self._register(client)
        response = client.post(
            "/api/auth/login", data={"username": "alice", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post(
            "/api/auth/login", data={"username": "ghost", "password": "password123"}
        )
        assert response.status_code == 401


class TestMe:
    def test_me_returns_current_user(self, client, auth_headers):
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "tester"

    def test_me_without_token(self, client):
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_me_with_garbage_token(self, client):
        response = client.get(
            "/api/users/me", headers={"Authorization": "Bearer not.a.jwt"}
        )
        assert response.status_code == 401
