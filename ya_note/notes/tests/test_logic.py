from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_authenticated_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        notes_count_before = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_url)

    def test_cannot_create_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        expected_error = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(
            response.context['form'],
            'slug',
            expected_error
        )
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_auto_slug_generation(self):
        """Slug формируется автоматически, если не заполнен."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        form_data_without_slug = {
            'title': 'Заголовок для авто-slug',
            'text': 'Текст заметки'
        }
        response = self.client.post(
            reverse('notes:add'),
            data=form_data_without_slug
        )
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(title=form_data_without_slug['title'])
        self.assertTrue(new_note.slug)

    def test_author_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_author_can_delete_own_note(self):
        """Пользователь может удалять свои заметки."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_user_cannot_edit_others_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.form_data['title'])

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.client.force_login(self.reader)
        notes_count_before = Note.objects.count()
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
