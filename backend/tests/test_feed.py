"""Feed tests: only followed users' posts, newest first, pagination."""

from tests.conftest import register_and_login


def make_post(client, headers, title, content="Content long enough for validation."):
    return client.post(
        "/api/posts", json={"title": title, "content": content}, headers=headers
    )


class TestFeed:
    def test_feed_requires_auth(self, client):
        assert client.get("/api/feed").status_code == 401

    def test_feed_only_shows_followed_users_posts(self, client, auth_headers):
        followed = register_and_login(client, "followed")
        stranger = register_and_login(client, "stranger")
        make_post(client, followed, "Post from followed")
        make_post(client, stranger, "Post from stranger")
        make_post(client, auth_headers, "My own post")  # own posts NOT in feed

        client.post("/api/users/followed/follow", headers=auth_headers)

        body = client.get("/api/feed", headers=auth_headers).json()
        titles = [p["title"] for p in body["items"]]
        assert titles == ["Post from followed"]
        assert body["total"] == 1

    def test_feed_empty_when_following_nobody(self, client, auth_headers):
        register_and_login(client, "someone")
        make_post(client, register_and_login(client, "someone2"), "Unseen post")
        body = client.get("/api/feed", headers=auth_headers).json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_feed_newest_first(self, client, auth_headers):
        followed = register_and_login(client, "followed")
        client.post("/api/users/followed/follow", headers=auth_headers)
        make_post(client, followed, "older post")
        make_post(client, followed, "newer post")

        titles = [
            p["title"]
            for p in client.get("/api/feed", headers=auth_headers).json()["items"]
        ]
        assert titles == ["newer post", "older post"]

    def test_feed_pagination(self, client, auth_headers):
        followed = register_and_login(client, "followed")
        client.post("/api/users/followed/follow", headers=auth_headers)
        for i in range(15):
            make_post(client, followed, f"post number {i:02d}")

        page1 = client.get("/api/feed?limit=10&offset=0", headers=auth_headers).json()
        assert len(page1["items"]) == 10
        assert page1["total"] == 15
        assert page1["limit"] == 10
        assert page1["offset"] == 0

        page2 = client.get("/api/feed?limit=10&offset=10", headers=auth_headers).json()
        assert len(page2["items"]) == 5

        # No overlap between pages
        ids1 = {p["id"] for p in page1["items"]}
        ids2 = {p["id"] for p in page2["items"]}
        assert ids1.isdisjoint(ids2)

    def test_feed_limit_capped_at_50(self, client, auth_headers):
        response = client.get("/api/feed?limit=100", headers=auth_headers)
        assert response.status_code == 422
