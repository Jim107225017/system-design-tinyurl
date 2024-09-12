from datetime import datetime, timedelta, timezone

from src.database.models import UrlCache, UrlRelation
from src.timing import get_current_ts


def test_create_tiny_url(client, mocker):
    mock_url_relation = UrlRelation(id=1, origin="https://example.com", tiny="abcdefgh", expired_date=datetime.now(timezone.utc) + timedelta(days=30))
    mocker.patch('src.database.actions.CrudHandler.create_tiny_url', return_value=mock_url_relation)

    response = client.post("/v1/tinyurl", json={"origin": "https://example.com"})
    assert response.status_code == 201
    data = response.json()
    print(data)
    assert data["tiny"] == f"http://testserver/v1/{mock_url_relation.tiny}"
    assert data["origin"] == mock_url_relation.origin
    assert data["success"] == True
    assert data["expired_date"] == mock_url_relation.expired_date.date().isoformat()


def test_create_tiny_url_invalid_url(client):
    response = client.post("/v1/tinyurl", json={"origin": f"https://g{'o'*2048}gle.com"})
    assert response.status_code == 422


def test_redirect_tiny_url_from_cache(client, mocker):
    mock_cache_data = UrlCache(origin="https://example.com", expired_date=get_current_ts() + 86400000)
    mocker.patch('src.database.actions.CrudHandler._CrudHandler__get_origin_url_in_cache', return_value=mock_cache_data)

    response = client.get("/v1/abcdefgh", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == mock_cache_data.origin


def test_redirect_tiny_url_success(client, mocker):
    mock_url_relation = UrlRelation(id=1, origin="https://example.com", tiny="abcdefgh", expired_date=datetime.now(timezone.utc) + timedelta(days=30))
    mocker.patch('src.database.actions.CrudHandler._CrudHandler__get_origin_url_in_sql', return_value=mock_url_relation)

    response = client.get("/v1/abcdefgh", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == mock_url_relation.origin


def test_redirect_nonexistent_tiny_url(client, mocker):
    mocker.patch('src.database.actions.CrudHandler._CrudHandler__get_origin_url_in_sql', return_value=None)

    response = client.get("/v1/nonexistent", allow_redirects=False)
    assert response.status_code == 404


def test_redirect_expired_tiny_url_from_cache(client, mocker):
    mock_cache_data = UrlCache(origin="https://example.com", expired_date=get_current_ts() - 86400000)
    mocker.patch('src.database.actions.CrudHandler._CrudHandler__get_origin_url_in_cache', return_value=mock_cache_data)

    response = client.get("/v1/expired", allow_redirects=False)
    assert response.status_code == 410


def test_redirect_expired_tiny_url(client, mocker):
    mock_url_relation = UrlRelation(id=1, origin="https://example.com", tiny="abcdefgh", expired_date=datetime.now(timezone.utc) - timedelta(days=30))
    mocker.patch('src.database.actions.CrudHandler._CrudHandler__get_origin_url_in_sql', return_value=mock_url_relation)

    response = client.get("/v1/expired", allow_redirects=False)
    assert response.status_code == 410


def test_redirect_tiny_url_server_error(client, mocker):
    mocker.patch('src.database.actions.CrudHandler._CrudHandler__decode_base62', side_effect=UnicodeError("Unexpected error"))

    response = client.get("/v1/error", allow_redirects=False)
    assert response.status_code == 500
