import pytest

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "news_count",
    ('8', '10', '12'),
)
def test_news_count_on_main_page(client, news_count):
    url = reverse('news:home')
    response = client.get(url)
    news_count = response.context['object_list']
    assert len(news_count) <= 10


@pytest.mark.django_db
def test_news_ordering(client):
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    news_dates = [news.date for news in news_list]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comments_ordering_on_news_page(client, pk_for_args_comments):
    url = reverse('news:detail', args=pk_for_args_comments)
    response = client.get(url)
    news = response.context['news']
    comments_set = news.comment_set.all()
    comments_dates = [comment.created for comment in comments_set]
    assert comments_dates == sorted(comments_dates)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_answer',
    [
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    ]
)
def test_pages_contains_form(
    parametrized_client,
    pk_for_args_news,
    expected_answer
):
    url = reverse('news:detail', args=pk_for_args_news)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is expected_answer
