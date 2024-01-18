import pytest
from http import HTTPStatus

from pytest_lazyfixture import lazy_fixture

pytestmark = pytest.mark.django_db

URLS_FOR_ANONYMOUS_USERS = (
    'home_url',
    'login_url',
    'logout_url',
    'signup_url',
    'detail_url'
)
URLS_FOR_AUTHORS = ('comment_edit_url', 'comment_delete_url')


@pytest.mark.parametrize('target_url', URLS_FOR_ANONYMOUS_USERS)
def test_availability_for_anonymous_user(request, client, target_url):
    url = request.getfixturevalue(target_url)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'target_url',
    URLS_FOR_ANONYMOUS_USERS + URLS_FOR_AUTHORS
)
@pytest.mark.parametrize(
    'client_role, client_fixture, expected_status',
    (
        ('author', lazy_fixture('author_client'), HTTPStatus.OK),
        (
            'other_author',
            lazy_fixture('another_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        ('anonym', lazy_fixture('client'), HTTPStatus.FOUND)
    )
)
def test_author_user_routes(
    request,
    client_role,
    client_fixture,
    target_url,
    expected_status
):
    url = request.getfixturevalue(target_url)
    response = client_fixture.get(url)
    if target_url in URLS_FOR_AUTHORS:
        if client_role == 'other_author':
            expected_status = HTTPStatus.NOT_FOUND
        elif client_role == 'anonym':
            expected_status = HTTPStatus.FOUND
    else:
        expected_status = HTTPStatus.OK

    assert response.status_code == expected_status
