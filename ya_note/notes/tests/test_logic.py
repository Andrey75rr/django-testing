from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from pytils.translit import slugify

from notes.models import Note
from .fixtures import (
    TestDataMixin,
    ADD_NOTE_URL,
    SUCCESS_URL,
    NOTE_EDIT_URL,
    NOTE_DELETE_URL,
    REDIRECT_ADD_NOTE_URL
)

User = get_user_model()


class TestLogic(TestDataMixin, TestCase):

    def test_authenticated_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        new_note_ids = note_ids_after - note_ids_before
        self.assertEqual(len(new_note_ids), 1)
        new_note_id = new_note_ids.pop()
        new_note = Note.objects.get(id=new_note_id)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(ADD_NOTE_URL, data=self.form_data)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(note_ids_after, note_ids_before)
        self.assertRedirects(response, REDIRECT_ADD_NOTE_URL)

    def test_cannot_create_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        expected_error = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(
            response.context['form'],
            'slug',
            expected_error
        )
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(note_ids_after, note_ids_before)

    def test_auto_slug_generation(self):
        """Slug формируется автоматически, если не заполнен."""
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        self.form_data.pop('slug')
        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note_ids_after = set(Note.objects.values_list('id', flat=True))
        new_note_ids = note_ids_after - note_ids_before
        self.assertEqual(len(new_note_ids), 1)
        new_note_id = new_note_ids.pop()
        new_note = Note.objects.get(id=new_note_id)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_own_note(self):
        """Пользователь может удалять свои заметки."""
        notes_count_before = Note.objects.count()
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        response = self.author_client.post(NOTE_DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cannot_edit_others_note(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалять чужие заметки."""
        notes_count_before = Note.objects.count()
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        response = self.reader_client.post(NOTE_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)
