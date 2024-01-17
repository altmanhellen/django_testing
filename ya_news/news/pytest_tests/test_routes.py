import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
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
LOGIN_URL = reverse('users:login')


@pytest.mark.parametrize('target_url', URLS_FOR_ANONYMOUS_USERS)
def test_availability_for_anonymous_user(request, client, target_url):
    url = request.getfixturevalue(target_url)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('target_url', URLS_FOR_AUTHORS)
@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('another_author_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('client'), LOGIN_URL)
    ]
)
def test_author_user_routes(
    request,
    client_fixture,
    target_url,
    expected_status
):
    url = request.getfixturevalue(target_url)
    response = client_fixture.get(url)

    if isinstance(expected_status, HTTPStatus):
        assert response.status_code == expected_status
    else:
        assertRedirects(
            response,
            expected_url=f'{expected_status}?next={url}'
        )
