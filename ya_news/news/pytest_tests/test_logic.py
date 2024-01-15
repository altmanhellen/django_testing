from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonym_cant_send_comment(client, news, form_data, pk_for_args_news):
    login_url = reverse('users:login')
    url = reverse('news:detail', args=pk_for_args_news)
    response = client.post(url, data=form_data)
    expected_status = f'{login_url}?next={url}'
    assertRedirects(response, expected_status)
    news.refresh_from_db()
    comments_set = news.comment_set.all()
    assert comments_set.count() == 0


@pytest.mark.django_db
def test_user_can_send_comment(
    admin_client,
    news,
    form_data,
    pk_for_args_news
):
    url = reverse('news:detail', args=pk_for_args_news)
    response = admin_client.post(url, data=form_data)
    expected_redirect_url = reverse(
        'news:detail',
        args=pk_for_args_news
    ) + '#comments'
    assertRedirects(response, expected_redirect_url)
    news.refresh_from_db()
    comments_set = news.comment_set.all()
    assert comments_set.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_comment_has_bad_words(
    admin_client,
    news,
    pk_for_args_news,
    form_data
):
    url = reverse('news:detail', args=pk_for_args_news)
    form_data['text'] = (
        f"Комментарий содержит запрещенное слово: {BAD_WORDS[0]}"
    )
    response = admin_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=[WARNING])
    news.refresh_from_db()
    comments_set = news.comment_set.all()
    assert comments_set.count() == 0


def test_user_can_edit_his_comment(
        author_client,
        comment,
        pk_for_args_comments,
        form_data
):
    url = reverse('news:edit', args=pk_for_args_comments)
    response = author_client.post(url, form_data)
    expected_redirect_url = reverse(
        'news:detail',
        args=pk_for_args_comments
    ) + '#comments'
    assertRedirects(response, expected_redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_can_delete_his_comment(author_client, pk_for_args_comments):
    url = reverse('news:delete', args=pk_for_args_comments)
    response = author_client.post(url)
    expected_redirect_url = reverse(
        'news:detail',
        args=pk_for_args_comments
    ) + '#comments'
    assertRedirects(response, expected_redirect_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_someoneelse_comment(
        admin_client,
        comment,
        form_data,
        pk_for_args_comments
):
    url = reverse('news:edit', args=pk_for_args_comments)
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_other_user_cant_delete_someoneelse_comment(
        admin_client,
        form_data,
        pk_for_args_comments
):
    url = reverse('news:delete', args=pk_for_args_comments)
    response = admin_client.post(url, form_data)
    expected_redirect_url = HTTPStatus.NOT_FOUND
    assert response.status_code == expected_redirect_url
