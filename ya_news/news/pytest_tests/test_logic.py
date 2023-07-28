from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


# Тест: анонимный пользователь не может создать комментарий
def test_anonymous_user_cant_create_comment(client, pk_from_news, form_data):
    url = reverse('news:detail', args=pk_from_news)
    initial_comment_count = Comment.objects.count()
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    final_comment_count = Comment.objects.count()
    assert initial_comment_count == final_comment_count


# Тест: пользователь может создать комментарий
def test_user_can_create_comment(admin_user, admin_client, news, form_data):
    url = reverse('news:detail', args=[news.pk])
    # Удаляем все существующие комментарии,
    # чтобы обеспечить пустое состояние базы данных
    Comment.objects.all().delete()
    initial_comment_count = Comment.objects.count()
    response = admin_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    final_comment_count = Comment.objects.count()
    assert initial_comment_count + 1 == final_comment_count
    new_comment = Comment.objects.last()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == admin_user


# Тест: пользователь не может использовать запрещенные слова в комментарии
def test_user_cant_use_bad_words(admin_client, pk_from_news):
    bad_words_data = {'text': f'Какой-то text, {choice(BAD_WORDS)}, еще text'}
    url = reverse('news:detail', args=pk_from_news)
    initial_comment_count = Comment.objects.count()
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    final_comment_count = Comment.objects.count()
    assert initial_comment_count == final_comment_count


# Тест: автор комментария может отредактировать свой комментарий
def test_author_can_edit_comment(
    author_client,
    pk_from_news,
    comment,
    form_data
):
    url = reverse('news:edit', args=[comment.pk])
    original_news = comment.news
    original_author = comment.author
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=pk_from_news) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == original_news
    assert comment.author == original_author


# Тест: автор комментария может удалить свой комментарий
def test_author_can_delete_comment(
        author_client,
        pk_from_news,
        pk_from_comment
):
    comment_id, = pk_from_comment
    url = reverse('news:delete', args=pk_from_comment)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=pk_from_news) + '#comments'
    assertRedirects(response, expected_url)
    comment_exists = Comment.objects.filter(pk=comment_id).exists()
    assert not comment_exists


# Тест: пользователь не может редактировать чужой комментарий
def test_other_user_cant_edit_comment(
    admin_client,
    pk_from_news,
    comment,
    form_data
):
    url = reverse('news:edit', args=[comment.pk])
    old_comment = comment.text
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment


# Тест: пользователь не может удалить чужой комментарий
def test_other_user_cant_delete_comment(
    admin_client,
    pk_from_news,
    pk_from_comment
):
    url = reverse('news:delete', args=pk_from_comment)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    expected_comments = 1
    assert comments_count == expected_comments
