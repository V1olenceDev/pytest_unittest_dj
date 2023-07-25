import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


# Тест: проверка количества новостей на домашней странице
@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_count(client):
    res = client.get(reverse('news:home'))
    comments_count = len(res.context['object_list'])
    assert comments_count == settings.NEWS_COUNT_ON_HOME_PAGE


# Тест: доступность формы комментария для различных пользователей
@pytest.mark.parametrize(
    'username, is_permitted', ((pytest.lazy_fixture('admin_client'), True),
                               (pytest.lazy_fixture('client'), False))
)
def test_comment_form_availability_for_different_users(pk_from_news, username,
                                                       is_permitted):
    res = username.get(reverse('news:detail', args=pk_from_news))
    context_form = res.context.get('form')
    assert (context_form is not None) == is_permitted
    if is_permitted:
        assert isinstance(context_form, CommentForm)


# Тест: проверка порядка отображения новостей на домашней странице
@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_order(client):
    res = client.get(reverse('news:home'))
    object_list = list(res.context['object_list'])
    sorted_list_of_news = sorted(object_list, key=lambda news: news.date,
                                 reverse=True)
    assert object_list == sorted_list_of_news


# Тест: проверка порядка отображения комментариев на странице новости
@pytest.mark.usefixtures('make_bulk_of_comments')
def test_comments_order(client, pk_from_news):
    url = reverse('news:detail', args=pk_from_news)
    res = client.get(url)
    object_list = res.context['news'].comment_set.all()
    sorted_list_of_comments = sorted(object_list,
                                     key=lambda comment: comment.created)
    for as_is, to_be in zip(object_list, sorted_list_of_comments):
        assert as_is.created == to_be.created
