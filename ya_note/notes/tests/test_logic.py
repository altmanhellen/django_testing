from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок заметки'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user
        )
        cls.url = reverse('notes:detail', args=(cls.notes.slug,))

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        create_url = reverse('notes:add')
        response = self.auth_client.post(create_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.title, self.NOTE_TITLE)
        self.assertEqual(new_note.text, self.NOTE_TEXT)
        self.assertEqual(new_note.author, self.user)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        non_unique_slug = self.notes.slug
        self.form_data['slug'] = non_unique_slug
        response = self.auth_client.post(url, self.form_data)
        full_error_message = non_unique_slug + WARNING
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=full_error_message
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug', None)
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.latest('slug')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        updated_data = {
            'title': 'Новый заголовок',
            'text': 'Обновленный текст заметки'
        }
        response = self.auth_client.post(url, updated_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, updated_data['title'])
        self.assertEqual(self.notes.text, updated_data['text'])

    def test_other_user_cant_edit_note(self):
        other_user = User.objects.create_user(username='Александр Дюма')
        other_client = Client()
        other_client.force_login(other_user)
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = other_client.post(url, self.form_data)
        self.assertNotEqual(response.status_code, 200)
        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
