def test_healthy_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.content.decode("utf-8") == "Hello World!"
