from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
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

        cls.add_url = reverse('notes:add')

    def test_note_in_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertTrue(note.title == 'Новость 2' for note in object_list)

    def test_other_user_notes_not_in_list(self):
        other_user = User.objects.create(username='Мимо шел')
        self.client.force_login(other_user)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 0)

    def test_add_page_response(self):
        self.client.force_login(self.author)
        create_url = reverse('notes:add')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_edit_page_has_form(self):
        self.client.force_login(self.author)
        note = Note.objects.first()
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
