import shutil
import tempfile

from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post, Group
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostsCreateFormTests.post_author,
            group=PostsCreateFormTests.group,
            text='Test text'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostsCreateFormTests.group,
        }
        Post.objects.create(
            author=PostsCreateFormTests.post_author,
            group=PostsCreateFormTests.group,
            text='Test text'
        )
        self.authorized_client.post(reverse('posts:post_create'),
                                    data=form_data,)
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Test text',
            'group': PostsCreateFormTests.group,
        }
        Post.objects.create(
            author=PostsCreateFormTests.post_author,
            group=PostsCreateFormTests.group,
            text='Test text'
        )
        self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'pk': self.post.id}), data=form_data,)
        var_for_resp = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response_2 = self.authorized_client.get(var_for_resp)
        form_fields = Post.objects.all()[:0]
        for value in form_fields:
            with self.subTest(value=value):
                response_2.context['post'][0].fields[value]
                self.assertEqual(form_fields, form_data)
