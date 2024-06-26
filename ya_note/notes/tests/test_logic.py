from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.forms import WARNING
from notes.models import Note

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
        cls.form_data = {
            'title': 'Form title',
            'text': 'Form text',
            'slug': 'form-slug'
        }
        cls.new_form_data = {
            'title': 'Updated title',
            'text': 'Updated text'
        }

    def create_note(self, author=None, **kwargs):
        default_data = {
            'title': 'Default title',
            'text': 'Default text',
            'slug': 'default-slug',
        }
        default_data.update(kwargs)
        author = author or self.author
        return Note.objects.create(author=author, **default_data)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_after = Note.objects.all()
        self.assertEqual(len(notes_after), 1)
        new_note = notes_after.first()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        Note.objects.all().delete()
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_url)
        notes_after = Note.objects.all()
        self.assertEqual(len(notes_after), 0)

    def test_slug_must_be_unique(self):
        self.create_note(title=self.form_data['title'],
                         text=self.form_data['text'],
                         slug=self.form_data['slug'])
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(response, form='form', field='slug',
                             errors=warning)

    def test_empty_slug(self):
        Note.objects.filter(title=self.form_data['title']).delete()
        del self.form_data['slug']
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(title=self.form_data['title'])
        self.assertIsNotNone(new_note.slug)
        self.assertNotEqual(new_note.slug, '')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        note = self.create_note(title='title', text='text',
                                slug='slug', author=self.author)
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.author_client.post(edit_url, self.new_form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(id=note.id)

        # Сравнить новые атрибуты заметки с атрибутами исходной заметки
        self.assertEqual(new_note.title, self.new_form_data['title'])
        self.assertEqual(new_note.text, self.new_form_data['text'])
        self.assertEqual(new_note.author, note.author)

    def test_other_user_cant_edit_note(self):
        note = self.create_note(title='title', text='text', slug='note-slug',
                                author=self.author)
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.reader_client.post(edit_url, self.new_form_data)
        self.assertEqual(response.status_code, 404)
        note_from_db = Note.objects.get(id=note.id)
        self.assertIsNotNone(note_from_db)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        note = Note.objects.create(title='title',
                                   text='text', slug='note-slug',
                                   author=self.author)
        delete_url = reverse('notes:delete', args=[note.slug])
        response = self.author_client.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        note_from_db = Note.objects.filter(id=note.id).exists()
        self.assertFalse(note_from_db)

    def test_other_user_cant_delete_note(self):
        note = Note.objects.create(title='title',
                                   text='text',
                                   slug='note-slug',
                                   author=self.author)
        delete_url = reverse('notes:delete', args=[note.slug])
        response = self.reader_client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        note_exists = Note.objects.filter(id=note.id).exists()
        self.assertTrue(note_exists)
