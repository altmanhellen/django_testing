import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Достоевский')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def another_author(django_user_model):
    return django_user_model.objects.create(username='Гоголь')


@pytest.fixture
def another_author_client(another_author, client):
    client.force_login(another_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def pk_for_args_news(news):
    return news.pk,


@pytest.fixture
def pk_for_args_comments(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'news': news,
        'text': 'Текст комментария',
        'author': author,
    }
