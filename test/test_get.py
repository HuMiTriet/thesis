import pytest


@pytest.mark.parametrize(
    ("id", "response_code"),
    (
        (1, 200),
        (2, 200),
        (3, 200),
    ),
)
def test_get_no_lock(client, id, response_code):
    response = client.get(f"/{id}")
    assert response.status_code == response_code
    assert response.json == {"id": id, "name": f"test{id}"}
