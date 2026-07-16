"""Post CRUD tests, including ownership rules and AI enrichment mocking."""

from tests.conftest import register_and_login


def make_post(client, headers, title="My Test Post", content="Some content long enough."):
    return client.post(
        "/api/posts", json={"title": title, "content": content}, headers=headers
    )


class TestCreatePost:
    def test_create_success(self, client, auth_headers):
        response = make_post(client, auth_headers)
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "My Test Post"
        assert body["author"]["username"] == "tester"
        assert "hashed_password" not in str(body)

    def test_create_runs_mocked_ai_enrichment(self, client, auth_headers):
        post_id = make_post(client, auth_headers).json()["id"]
        # TestClient runs BackgroundTasks synchronously before returning,
        # so the mocked summary/tags are already persisted.
        body = client.get(f"/api/posts/{post_id}").json()
        assert body["summary"] == "A mocked TL;DR of the post."
        assert body["tags"] == ["testing", "python", "mocked"]

    def test_create_requires_auth(self, client):
        response = client.post(
            "/api/posts", json={"title": "Nope", "content": "No token, no post."}
        )
        assert response.status_code == 401

    def test_create_short_title_rejected(self, client, auth_headers):
        response = make_post(client, auth_headers, title="ab")
        assert response.status_code == 422

    def test_create_short_content_rejected(self, client, auth_headers):
        response = make_post(client, auth_headers, content="tiny")
        assert response.status_code == 422


class TestReadPost:
    def test_get_post_public(self, client, auth_headers):
        post_id = make_post(client, auth_headers).json()["id"]
        response = client.get(f"/api/posts/{post_id}")  # no auth header
        assert response.status_code == 200

    def test_get_missing_post_404(self, client):
        response = client.get("/api/posts/99999")
        assert response.status_code == 404


class TestUpdatePost:
    def test_author_can_edit(self, client, auth_headers):
        post_id = make_post(client, auth_headers).json()["id"]
        response = client.put(
            f"/api/posts/{post_id}",
            json={"title": "Updated Title", "content": "Updated content here."},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_non_owner_gets_403(self, client, auth_headers):
        post_id = make_post(client, auth_headers).json()["id"]
        intruder = register_and_login(client, "intruder")
        response = client.put(
            f"/api/posts/{post_id}",
            json={"title": "Hijacked", "content": "This is not my post."},
            headers=intruder,
        )
        assert response.status_code == 403


class TestDeletePost:
    def test_author_can_delete_204(self, client, auth_headers):
        post_id = make_post(client, auth_headers).json()["id"]
        response = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
        assert response.status_code == 204
        assert client.get(f"/api/posts/{post_id}").status_code == 404

    def test_non_owner_delete_403(self, client, auth_headers):
        post_id = make_post(client, auth_headers).json()["id"]
        intruder = register_and_login(client, "intruder")
        response = client.delete(f"/api/posts/{post_id}", headers=intruder)
        assert response.status_code == 403
