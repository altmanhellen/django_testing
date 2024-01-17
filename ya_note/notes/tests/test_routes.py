from http import HTTPStatus

from django.contrib.auth import get_user_model

from .common_test import BaseTestWithUrls

User = get_user_model()


class TestRoutes(BaseTestWithUrls):

    def test_anonymous_redirects(self):
        urls = (
            self.ADD_URL,
            self.EDIT_URL(self.note.slug),
            self.DELETE_URL(self.note.slug),
            self.DETAIL_URL(self.note.slug),
            self.LIST_URL
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_user_access(self):
        user_urls = (
            (
                self.author, (
                    (self.LIST_URL, None),
                    (self.ADD_URL, None),
                    (self.EDIT_URL(self.note.slug), None),
                    (self.DELETE_URL(self.note.slug), None),
                    (self.DETAIL_URL(self.note.slug), None),
                ), HTTPStatus.OK),
            (
                self.reader,
                (
                    (self.LIST_URL, None),
                    (self.ADD_URL, None),
                ), HTTPStatus.OK),
            (
                self.reader,
                (
                    (self.DETAIL_URL(self.note.slug), None),
                    (self.EDIT_URL(self.note.slug), None),
                    (self.DELETE_URL(self.note.slug), None),
                ), HTTPStatus.NOT_FOUND
            ),
        )
        for user, routes, expected_status in user_urls:
            self.client.force_login(user)
            for url, args in routes:
                if args:
                    url = url(self.note.slug)
                with self.subTest(user=user.username, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)
