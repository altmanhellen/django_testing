from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from .conftest import FORM_DATA
from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db

FORM_DATA_COPY = FORM_DATA.copy()


@pytest.mark.django_db
class TestUserAccessToComment:
    pytestmark = pytest.mark.django_db

    @pytest.mark.parametrize(
        'target_url, target_login_url',
        (
            ('detail_url', 'login_url'),
        )
    )
    def test_anonym_cant_send_comment(
        self,
        request,
        client,
        news,
        target_login_url,
        target_url
    ):
        news_object, news_pk = news
        FORM_DATA_COPY['news'] = news_object
        FORM_DATA_COPY['author'] = client
        initial_comments_count = Comment.objects.count()
        login_url = request.getfixturevalue(target_login_url)
        url = request.getfixturevalue(target_url)
        response = client.post(url, data=FORM_DATA_COPY)
        expected_status = f'{login_url}?next={url}'
        assertRedirects(response, expected_status)
        news_object.refresh_from_db()
        comments_set = news_object.comment_set.all()
        assert comments_set.count() == initial_comments_count

    @pytest.mark.parametrize(
        'target_url',
        ('detail_url',)
    )
    def test_user_can_send_comment(
        self,
        request,
        admin_client,
        news,
        target_url
    ):
        news_object, news_pk = news
        FORM_DATA_COPY['news'] = news_object
        FORM_DATA_COPY['author'] = admin_client
        initial_comments_count = news_object.comment_set.count()
        url = request.getfixturevalue(target_url)
        response = admin_client.post(url, data=FORM_DATA_COPY)
        expected_redirect_url = '{}#comments'.format(url)
        assertRedirects(response, expected_redirect_url)
        new_comments_count = news_object.comment_set.count()
        assert new_comments_count == initial_comments_count + 1

    @pytest.mark.parametrize(
        'action, target_url, expected_redirect_target_url',
        (
            ('edit', 'comment_edit_url', 'detail_url'),
            ('delete', 'comment_delete_url', 'detail_url'),
        )
    )
    def test_user_can_edit_or_delete_his_comment(
        self,
        request,
        author_client,
        comment,
        news,
        action,
        target_url,
        expected_redirect_target_url
    ):
        news_object, news_pk = news
        comment_object, comment_pk = comment
        url = request.getfixturevalue(target_url)
        expected_redirect_url = request.getfixturevalue(
            expected_redirect_target_url
        )
        if action == 'edit':
            FORM_DATA_COPY['news'] = news_object
            FORM_DATA_COPY['comment'] = comment_object
            FORM_DATA_COPY['author'] = author_client
            response = author_client.post(url, FORM_DATA_COPY)
        else:
            response = author_client.post(url)

        expected_redirect_url = '{}#comments'.format(expected_redirect_url)
        assertRedirects(response, expected_redirect_url)

        if action == 'edit':
            comment_object.refresh_from_db()
            updated_comment = Comment.objects.get(pk=comment_pk)
            assert updated_comment.text == FORM_DATA_COPY['text']
            assert updated_comment.news.id == news_object.id
        else:
            with pytest.raises(Comment.DoesNotExist):
                Comment.objects.get(pk=comment_pk)

    @pytest.mark.parametrize(
        'action, target_url',
        [
            ('edit', 'comment_edit_url'),
            ('delete', 'comment_delete_url')
        ]
    )
    def test_user_cant_edit_or_delete_someoneelse_comment(
        self,
        request,
        admin_client,
        news,
        comment,
        another_author_client,
        action,
        target_url
    ):
        news_object, news_pk = news
        comment_object, comment_pk = comment
        FORM_DATA_COPY['news'] = news_object
        FORM_DATA_COPY['comment'] = comment_object

        if action == 'edit':
            FORM_DATA_COPY['author'] = another_author_client
            expected_status = HTTPStatus.NOT_FOUND
        else:
            FORM_DATA_COPY['author'] = admin_client
            expected_status = HTTPStatus.NOT_FOUND

        url = request.getfixturevalue(target_url)
        response = admin_client.post(url, FORM_DATA_COPY)
        assert response.status_code == expected_status

        if action == 'edit':
            comment_from_db = Comment.objects.get(id=comment_object.id)
            assert comment_object.text == comment_from_db.text


@pytest.mark.django_db
class TestFilterComment:
    pytestmark = pytest.mark.django_db

    @pytest.mark.parametrize(
        'target_url',
        ('detail_url',)
    )
    def test_comment_has_bad_words(
        self,
        request,
        admin_client,
        news,
        target_url
    ):
        news_object, news_pk = news
        FORM_DATA_COPY['news'] = news_object
        FORM_DATA_COPY['author'] = admin_client
        url = request.getfixturevalue(target_url)
        FORM_DATA_COPY['text'] = (
            'Комментарий содержит запрещенное слово: {}'.format(BAD_WORDS[0])
        )
        response = admin_client.post(url, data=FORM_DATA_COPY)
        assertFormError(response, 'form', 'text', errors=WARNING)
        news_object.refresh_from_db()
        comments_set = news_object.comment_set.all()
        assert comments_set.count() == 0
