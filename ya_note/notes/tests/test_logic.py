from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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

    def create_note(self, **kwargs):
        default_data = {
            'title': 'Default title',
            'text': 'Default text',
            'slug': 'default-slug',
            'author': self.author
        }
        default_data.update(kwargs)
        return Note.objects.create(**default_data)

    def test_user_can_create_note(self):
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        # Получаем только что созданную заметку, используя предоставленный slug
        new_note_slug = self.form_data['slug']
        new_note = Note.objects.get(slug=new_note_slug)
        # Проверяем атрибуты новой заметки
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_url)
        notes = Note.objects.filter(title=self.form_data['title'])
        self.assertEqual(len(notes), 0)

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
        del self.form_data['slug']
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes = Note.objects.filter(title=self.form_data['title'])
        self.assertEqual(len(notes), 1)

    def test_author_can_edit_note(self):
        note = self.create_note(title='title', text='text',
                                slug='note-slug')
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.author_client.post(edit_url, self.new_form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get(id=note.id)
        self.assertEqual(new_note.title, self.new_form_data['title'])
        self.assertEqual(new_note.text, self.new_form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        note = Note.objects.create(title='title', text='text',
                                   slug='note-slug', author=self.author)
        edit_url = reverse('notes:edit', args=[note.slug])
        response = self.reader_client.post(edit_url, self.new_form_data)
        self.assertEqual(response.status_code, 404)
        note_from_db = Note.objects.get(id=note.id)
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
        note_from_db = Note.objects.filter(id=note.id).first()
        self.assertIsNotNone(note_from_db)
