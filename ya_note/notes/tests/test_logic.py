from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreationAndEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {'title': 'Form title',
                         'text': 'Form text', 'slug': 'form-slug'}
        cls.new_form_data = {'title': 'Updated title', 'text': 'Updated text'}

    def test_user_can_create_note(self):
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        expected_notes_count = 1
        self.assertEqual(Note.objects.count(), expected_notes_count)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_url)
        expected_notes_count = 0
        self.assertEqual(Note.objects.count(), expected_notes_count)

    def test_slug_must_be_unique(self):
        self.author_client.post(reverse('notes:add'), data=self.form_data)
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(response, form='form', field='slug',
                             errors=warning)

    def test_empty_slug(self):
        del self.form_data['slug']
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        expected_notes_count = 1
        self.assertEqual(Note.objects.count(), expected_notes_count)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.get(slug=expected_slug)
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        note = Note.objects.create(title='title', text='text',
                                   slug='note-slug', author=self.author)
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.author_client.post(edit_url, self.new_form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        self.assertEqual(note.title, self.new_form_data['title'])
        self.assertEqual(note.text, self.new_form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_other_user_cant_edit_note(self):
        note = Note.objects.create(title='title', text='text',
                                   slug='note-slug', author=self.author)
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.reader_client.post(edit_url, self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.filter(id=note.id).first()
        self.assertIsNotNone(note_from_db)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        note = Note.objects.create(title='title',
                                   text='text', slug='note-slug',
                                   author=self.author)
        delete_url = reverse('notes:delete', args=[note.slug])
        response = self.author_client.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)
        note_from_db = Note.objects.filter(id=note.id).first()
        self.assertIsNone(note_from_db)

    def test_other_user_cant_delete_note(self):
        # Test on preventing other users from deleting a note
        note = Note.objects.create(title='title',
                                   text='text',
                                   slug='note-slug',
                                   author=self.author)
        delete_url = reverse('notes:delete', args=[note.slug])
        response = self.reader_client.post(delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        note_from_db = Note.objects.filter(id=note.id).first()
        self.assertIsNotNone(note_from_db)
