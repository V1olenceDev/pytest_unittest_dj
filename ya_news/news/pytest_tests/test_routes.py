from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


# Общая функция для проверки страниц
def check_page_availability(client, page, args, expected_status):
    url = reverse(page, args=args)
    response = client.get(url)
    assert response.status_code == expected_status


# Тест: доступность страниц для различных пользователей
@pytest.mark.parametrize(
    'page, args, expected_status',
    [
        ('news:home', None, HTTPStatus.OK),
        ('users:login', None, HTTPStatus.OK),
        ('users:logout', None, HTTPStatus.OK),
        ('users:signup', None, HTTPStatus.OK),
        ('news:detail', pytest.lazy_fixture('pk_from_news'), HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('pk_from_comment'), HTTPStatus.OK),
        ('news:delete', pytest.lazy_fixture('pk_from_comment'), HTTPStatus.OK)
    ]
)
@pytest.mark.django_db
def test_pages_availability(client,
                            author_client,
                            admin_client,
                            page,
                            args,
                            expected_status,
                            pk_from_comment):
    if client == admin_client:
        expected_status = HTTPStatus.NOT_FOUND
    check_page_availability(client, page, args, expected_status)


# Тест: проверка редиректа на страницы аутентификации
@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, args',
    [
        ('news:edit', pytest.lazy_fixture('pk_from_comment')),
        ('news:delete', pytest.lazy_fixture('pk_from_comment'))
    ]
)
def test_redirects(client, page, args):
    login_url = reverse('users:login')
    url = reverse(page, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
