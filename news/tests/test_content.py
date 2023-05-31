import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(add_many_news, admin_client):
    url = reverse('news:home')
    response = admin_client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(add_many_news, admin_client):
    url = reverse('news:home')
    response = admin_client.get(url)
    object_list = response.context['object_list']
    first_news_date = object_list[0].date
    all_dates = [news.date for news in object_list]
    assert first_news_date == max(all_dates)


@pytest.mark.django_db
def test_comments_order(add_many_comments, news_id, author_client):
    url = reverse('news:detail', args=news_id)
    response = author_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
@pytest.mark.django_db
def test_pages_contains_form(parametrized_client, form_in_context, news_id):
    url = reverse('news:detail', args=news_id)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
