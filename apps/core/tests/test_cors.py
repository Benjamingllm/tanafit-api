def test_authorize_declared_origin(client, settings):
    settings.CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
    response = client.get("/api/health/", headers={"Origin": "http://localhost:5173"})
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"


def test_refuse_unknown_origin(client, settings):
    settings.CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
    response = client.get("/api/health/", headers={"Origin": "http://localhost:9999"})
    assert "Access-Control-Allow-Origin" not in response.headers
