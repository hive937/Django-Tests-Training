import shutil
import tempfile

from posts.forms import PostForm
from posts.models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            text='Тестовый текст',
            group='Тестовая группа',
        )
        cls.form = TaskCreateForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(Posts.objects.count(), tasks_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый текст',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(Posts.objects.count(), tasks_count + 1)

