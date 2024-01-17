import pytest
from django.test import Client
from django.urls import reverse

from news.models import News, Comment

FORM_DATA = {
    'news': None,
    'text': 'Текст комментария',
    'author': None,
}


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Достоевский')


@pytest.fixture
def author_client(author):
    client_author = Client()
    client_author.force_login(author)
    return client_author


@pytest.fixture
def another_author(django_user_model):
    return django_user_model.objects.create(username='Гоголь')


@pytest.fixture
def another_author_client(another_author):
    other_client_author = Client()
    other_client_author.force_login(another_author)
    return other_client_author


@pytest.fixture
def news():
    news_object = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news_object, news_object.pk


@pytest.fixture
def comment(author, news):
    news_object, _ = news
    comment_object = Comment.objects.create(
        news=news_object,
        text='Текст комментария',
        author=author,
    )
    return comment_object, comment_object.pk


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    news_object, news_pk = news
    return reverse('news:detail', args=(news_pk, ))


@pytest.fixture
def news_edit_url(news):
    news_object, news_pk = news
    return reverse('news:edit', args=(news_pk, ))


@pytest.fixture
def news_delete_url(news):
    news_object, news_pk = news
    return reverse('news:delete', args=(news_pk, ))


@pytest.fixture
def comment_edit_url(comment):
    comment_object, comment_pk = comment
    return reverse('news:edit', args=(comment_pk, ))


@pytest.fixture
def comment_delete_url(comment):
    comment_object, comment_pk = comment
    return reverse('news:delete', args=(comment_pk, ))
