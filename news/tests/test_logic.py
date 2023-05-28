from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news_id, form_data, client):
    url = reverse('news:detail', args=news_id)
    client.post(url, form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, news_id, form_data):
    url = reverse('news:detail', args=news_id)
    author_client.post(url, form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(form_data, author_client, news_id):
    url = reverse('news:detail', args=news_id)
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(url, data=form_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(form_data, add_comment):
    add_comment.refresh_from_db()
    assert add_comment.text == form_data['text']


def test_other_user_cant_edit_note(admin_client, form_data, add_comment):
    url = reverse('news:edit', args=(add_comment.news_id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get()
    assert add_comment.text == comment_from_db.text
    assert add_comment.author == comment_from_db.author


def test_author_can_delete_comment(author_client, comment_id):
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, comment_id):
    url = reverse('news:delete', args=comment_id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
