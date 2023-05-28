import pytest
from datetime import datetime, timedelta

from django.utils import timezone

from yanews import settings
from news.models import Comment, News
from news.forms import BAD_WORDS


@pytest.fixture
def news():
    news = News.objects.create(
        title='Title',
        text='Text',
        date=datetime.today()
    )
    return news


@pytest.fixture
def add_many_news():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
            )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def add_many_comments(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def add_comment(author, news):
    comment = Comment.objects.create(
        text='Текст',
        author=author,
        news_id=news.id
    )
    return comment


@pytest.fixture
def comment_id(add_comment):
    return add_comment.id,


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def form_data():
    return {
        'text': 'Текст',
        'author': 'Автор',
    }


@pytest.fixture
def comment_wiht_bad_words(author, news_id):
    comment = Comment.objects.create(
        text=f'Какой-то текст, {BAD_WORDS[0]}, еще текст',
        author=author,
        news_id=news_id
    )
    return comment
