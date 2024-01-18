import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


class TestNewsAndCommentsContent:

    @pytest.mark.parametrize(
        'news_count', (8, 10, 12),
    )
    def test_news_count_on_main_page(
        self,
        request,
        client,
        news_count
    ):
        url = request.getfixturevalue('home_url')
        response = client.get(url)
        news_count = response.context['object_list']
        assert len(news_count) <= 10

    def test_news_ordering(self, request, client):
        url = request.getfixturevalue('home_url')
        response = client.get(url)
        news_list = response.context['object_list']
        news_dates = [news.date for news in news_list]
        assert news_dates == sorted(news_dates, reverse=True)

    def test_comments_ordering_on_news_page(
        self,
        request,
        client
    ):
        url = request.getfixturevalue('detail_url')
        response = client.get(url)
        news = response.context['news']
        comments_set = news.comment_set.all()
        comments_dates = [comment.created for comment in comments_set]
        assert comments_dates == sorted(comments_dates)

    @pytest.mark.parametrize(
        'parametrized_client, expected_answer',
        (
            (pytest.lazy_fixture('client'), False),
            (pytest.lazy_fixture('admin_client'), True),
        )
    )
    def test_pages_contains_form(
        self,
        request,
        parametrized_client,
        expected_answer
    ):
        url = request.getfixturevalue('detail_url')
        response = parametrized_client.get(url)
        if 'form' in response.context:
            assert isinstance(
                response.context['form'],
                CommentForm
            ) == expected_answer
        else:
            assert not expected_answer
