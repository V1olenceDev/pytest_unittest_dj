from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, args, expected_status',
    [
        ('news:home', None, HTTPStatus.OK),
        ('users:login', None, HTTPStatus.OK),
        ('users:logout', None, HTTPStatus.OK),
        ('users:signup', None, HTTPStatus.OK),
        ('news:detail', pytest.lazy_fixture('pk_from_news'), HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('pk_from_comment'), None),
        ('news:delete', pytest.lazy_fixture('pk_from_comment'), None)
    ]
)
def test_pages_status_codes(client, page, args, expected_status):
    url = reverse(page, args=args)
    response = client.get(url)

    if expected_status:
        assert response.status_code == expected_status
    else:
        assert response.status_code != HTTPStatus.OK


# Тест: проверка перенаправления на страницу входа для защищенных страниц
@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, args',
    [
        ('news:edit', pytest.lazy_fixture('pk_from_comment')),
        ('news:delete', pytest.lazy_fixture('pk_from_comment'))
    ]
)
def test_protected_pages_redirect_to_login(client, page, args):
    url = reverse(page, args=args)
    response = client.get(url)
    assertRedirects(response, reverse('users:login') + f'?next={url}')
