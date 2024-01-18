from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy
from notes.models import Note

User = get_user_model()


class BaseTestForCommonUrls:

    @classmethod
    def setUpTestData(cls):
        cls.LIST_URL = reverse_lazy('notes:list')
        cls.ADD_URL = reverse_lazy('notes:add')
        cls.LOGIN_URL = reverse_lazy('users:login')
        cls.SUCCESS = reverse_lazy('notes:success')
        cls.EDIT_URL = lambda slug: reverse_lazy('notes:edit', args=(slug,))
        cls.DELETE_URL = lambda slug: reverse_lazy(
            'notes:delete',
            args=(slug,)
        )
        cls.DETAIL_URL = lambda slug: reverse_lazy(
            'notes:detail',
            args=(slug,)
        )


class BaseTestForCreateNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        notes = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.',
                slug=f'news{index}',
                author=cls.author
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(notes)


class CommonTest(BaseTestForCommonUrls, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        notes = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.',
                slug=f'news{index}',
                author=cls.author
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(notes)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.author)


class BaseTest(BaseTestForCommonUrls, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = cls.create_auth_client(cls.user)

    @staticmethod
    def create_auth_client(user):
        client = Client()
        client.force_login(user)
        return client

    def setUp(self):
        super().setUp()
        self.auth_client = self.create_auth_client(self.user)


class BaseTestWithUrls(BaseTestForCommonUrls, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        notes = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.',
                slug=f'news{index}',
                author=cls.author
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(notes)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
