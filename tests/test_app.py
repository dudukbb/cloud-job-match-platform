def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code in (200, 503)  # 503 acceptable when Redis not available
    data = resp.get_json()
    assert "status" in data
    assert "checks" in data


def test_jobs_list_redirects_or_200(client):
    resp = client.get("/jobs/")
    assert resp.status_code == 200


def test_register_get(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200
    assert b"Create Account" in resp.data


def test_login_get(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert b"Sign In" in resp.data


def test_register_and_login(client):
    # Register
    resp = client.post("/auth/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Secur3Pass!",
        "confirm_password": "Secur3Pass!",
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Login
    resp = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "Secur3Pass!",
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_protected_route_redirects(client):
    resp = client.get("/jobs/create")
    assert resp.status_code == 302  # redirect to login


def test_jobs_list_when_redis_unavailable(client, monkeypatch):
    import app.extensions as ext
    from app.models import Job

    class FailingRedis:
        def get(self, _key):
            raise RuntimeError("redis down")

        def setex(self, _key, _ttl, _value):
            raise RuntimeError("redis down")

        def scan_iter(self, _pattern):
            return iter(())

        def delete(self, _key):
            return 0

    class FakePagination:
        items = []
        has_next = False
        has_prev = False
        total = 0

    class FakeQuery:
        def filter_by(self, **_kwargs):
            return self

        def filter(self, *_args, **_kwargs):
            return self

        def order_by(self, *_args, **_kwargs):
            return self

        def paginate(self, **_kwargs):
            return FakePagination()

    monkeypatch.setattr(ext, "redis_client", FailingRedis())
    monkeypatch.setattr(Job, "query", FakeQuery())

    resp = client.get("/jobs/")
    assert resp.status_code == 200
