from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from notes.forms import NoteForm
from notes.models import Note
from .common_test import CommonTest

User = get_user_model()


class TestListPage(CommonTest):

    def test_note_in_list(self):
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertTrue(any(note.title == 'Новость 2' for note in object_list))

    def test_other_user_notes_not_in_list(self):
        other_user = User.objects.create(username='Мимо шел')
        self.client.force_login(other_user)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)

    def test_add_page_response(self):
        response = self.client.get(self.ADD_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_has_form(self):
        note = Note.objects.first()
        edit_url = reverse_lazy('notes:edit', args=(note.slug, ))
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)
