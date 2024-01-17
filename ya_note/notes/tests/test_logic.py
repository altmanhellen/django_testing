from http import HTTPStatus

from django.contrib.auth.models import User
from django.urls import reverse_lazy
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .common_test import BaseTest


class TestNoteCreation(BaseTest):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок заметки'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT}
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user
        )
        cls.url = reverse_lazy('notes:detail', args=(cls.notes.slug,))

    def _test_note_creation_with_slug(self, slug=None):
        url = reverse_lazy('notes:add')
        form_data = self.form_data.copy()
        if slug is not None:
            form_data['slug'] = slug
        else:
            form_data.pop('slug', None)

        initial_count = Note.objects.count()
        response = self.auth_client.post(url, form_data)
        self.assertRedirects(response, reverse_lazy('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count + 1)

        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        if slug is None:
            expected_slug = slugify(form_data['title'])
            self.assertEqual(new_note.slug, expected_slug)

    def test_anonymous_user_cant_create_note(self):
        initial_count = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        new_count = Note.objects.count()
        self.assertEqual(new_count, initial_count)

    def test_user_can_create_note(self):
        self._test_note_creation_with_slug()

    def test_not_unique_slug(self):
        url = reverse_lazy('notes:add')
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
        self._test_note_creation_with_slug(slug='')

    def test_author_can_edit_note(self):
        initial_count = Note.objects.count()
        url = reverse_lazy('notes:edit', args=(self.notes.slug, ))
        updated_data = {
            'title': 'Новый заголовок',
            'text': 'Обновленный текст заметки'
        }
        response = self.auth_client.post(url, updated_data)
        self.assertRedirects(response, reverse_lazy('notes:success'))
        updated_note = Note.objects.get(pk=self.notes.pk)
        self.assertEqual(updated_note.title, updated_data['title'])
        self.assertEqual(updated_note.text, updated_data['text'])
        new_count = Note.objects.count()
        self.assertEqual(new_count, initial_count)

    def test_other_user_cant_edit_note(self):
        other_user = User.objects.create_user(username='Александр Дюма')
        other_client = self.create_auth_client(other_user)
        url = reverse_lazy('notes:edit', args=(self.notes.slug, ))
        response = other_client.post(url, self.form_data)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
