from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):
    URL_NOTE = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.form_data = {'title': 'Form title',
                         'text': 'Form text',
                         'slug': 'form-slug'}

    def test_user_can_create_note(self):
        # Тест на создание заметки аутентифицированным пользователем
        self.client.force_login(self.author)
        response = self.client.post(self.URL_NOTE, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        expected_notes_count = 1
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)

        new_note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        # Тест на невозможность создания заметки анонимным пользователем
        response = self.client.post(self.URL_NOTE, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.URL_NOTE}'
        self.assertRedirects(response, expected_url)
        expected_notes_count = 0
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)

    def test_slug_must_be_unique(self):
        # Тест на уникальность слага
        self.client.force_login(self.author)
        self.client.post(self.URL_NOTE, data=self.form_data)
        res = self.client.post(self.URL_NOTE, data=self.form_data)
        warn = self.form_data['slug'] + WARNING
        self.assertFormError(res, form='form', field='slug', errors=warn)

    def test_empty_slug(self):
        # Тест на создание слага из заголовка, если слаг не указан
        self.client.force_login(self.author)
        del self.form_data['slug']
        res = self.client.post(self.URL_NOTE, data=self.form_data)
        self.assertRedirects(res, reverse('notes:success'))
        expected_notes_count = 1
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)

        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.filter(slug=expected_slug).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    TITLE = 'title'
    NEW_TITLE = 'updated title'
    TEXT = 'text'
    NEW_TEXT = 'updated text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug='note-slug',
            author=cls.author,
        )
        cls.edit_note_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_note_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT}

    def test_author_can_edit_note(self):
        # Тест на редактирование заметки автором
        self.author_client.post(self.edit_note_url, self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_other_user_cant_edit_note(self):
        # Тест на невозможность редактирования заметки другим пользователем
        res = self.reader_client.post(self.edit_note_url, self.form_data)
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.filter(id=self.note.id).first()
        self.assertIsNotNone(note_from_db)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        # Тест на удаление заметки автором
        res = self.author_client.post(self.delete_note_url)
        self.assertRedirects(res, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        # Тест на невозможность удаления заметки другим пользователем
        res = self.reader_client.post(self.delete_note_url)
        self.assertEqual(res.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
