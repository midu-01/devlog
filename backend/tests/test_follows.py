"""Follow system tests: follow/unfollow, self-follow, duplicates, counts."""

from tests.conftest import register_and_login


class TestFollow:
    def test_follow_success(self, client, auth_headers):
        register_and_login(client, "target")
        response = client.post("/api/users/target/follow", headers=auth_headers)
        assert response.status_code == 204

    def test_self_follow_400(self, client, auth_headers):
        response = client.post("/api/users/tester/follow", headers=auth_headers)
        assert response.status_code == 400

    def test_duplicate_follow_409(self, client, auth_headers):
        register_and_login(client, "target")
        client.post("/api/users/target/follow", headers=auth_headers)
        response = client.post("/api/users/target/follow", headers=auth_headers)
        assert response.status_code == 409

    def test_follow_missing_user_404(self, client, auth_headers):
        response = client.post("/api/users/ghost/follow", headers=auth_headers)
        assert response.status_code == 404

    def test_follow_requires_auth(self, client):
        register_and_login(client, "target")
        response = client.post("/api/users/target/follow")
        assert response.status_code == 401


class TestUnfollow:
    def test_unfollow_success(self, client, auth_headers):
        register_and_login(client, "target")
        client.post("/api/users/target/follow", headers=auth_headers)
        response = client.delete("/api/users/target/follow", headers=auth_headers)
        assert response.status_code == 204

    def test_unfollow_when_not_following_404(self, client, auth_headers):
        register_and_login(client, "target")
        response = client.delete("/api/users/target/follow", headers=auth_headers)
        assert response.status_code == 404


class TestFollowerLists:
    def test_followers_and_following_with_counts(self, client, auth_headers):
        register_and_login(client, "target")
        client.post("/api/users/target/follow", headers=auth_headers)

        followers = client.get("/api/users/target/followers").json()
        assert followers["total"] == 1
        assert followers["items"][0]["username"] == "tester"

        following = client.get("/api/users/tester/following").json()
        assert following["total"] == 1
        assert following["items"][0]["username"] == "target"

        # target follows nobody
        assert client.get("/api/users/target/following").json()["total"] == 0
