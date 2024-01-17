import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestNewsAndCommentsContent:
    pytestmark = pytest.mark.django_db

    @pytest.mark.parametrize(
        'target_url, news_count',
        (
            ('home_url', 8),
            ('home_url', 10),
            ('home_url', 12)
        ),
    )
    def test_news_count_on_main_page(
        self,
        request,
        client,
        target_url,
        news_count
    ):
        url = request.getfixturevalue(target_url)
        response = client.get(url)
        news_count = response.context['object_list']
        assert len(news_count) <= 10

    @pytest.mark.parametrize(
        'target_url',
        ('home_url',)
    )
    def test_news_ordering(self, request, client, target_url):
        url = request.getfixturevalue(target_url)
        response = client.get(url)
        news_list = response.context['object_list']
        news_dates = [news.date for news in news_list]
        assert news_dates == sorted(news_dates, reverse=True)

    @pytest.mark.parametrize(
        'target_url',
        ('detail_url',)
    )
    def test_comments_ordering_on_news_page(
        self,
        request,
        client,
        target_url
    ):
        url = request.getfixturevalue(target_url)
        response = client.get(url)
        news = response.context['news']
        comments_set = news.comment_set.all()
        comments_dates = [comment.created for comment in comments_set]
        assert comments_dates == sorted(comments_dates)

    @pytest.mark.parametrize(
        'target_url, parametrized_client, expected_answer',
        (
            ('detail_url', pytest.lazy_fixture('client'), False),
            ('detail_url', pytest.lazy_fixture('admin_client'), True),
        )
    )
    def test_pages_contains_form(
        self,
        request,
        target_url,
        parametrized_client,
        expected_answer
    ):
        url = request.getfixturevalue(target_url)
        response = parametrized_client.get(url)
        if 'form' in response.context:
            assert isinstance(
                response.context['form'],
                CommentForm
            ) == expected_answer
        else:
            assert not expected_answer
