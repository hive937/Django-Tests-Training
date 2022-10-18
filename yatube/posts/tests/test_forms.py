import shutil
import tempfile

from posts.forms import PostForm
from posts.models import Post, Group, User
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.random_user = User.objects.create(
            username='random_user'
        )
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug-2',
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.post_author)
        self.authorized_client_2.force_login(self.random_user)

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

    def test_edit_post_with_group_change(self):
        form_data = {
            'text': 'Test text',
            'group': PostsCreateFormTests.group_2,
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

    def test_create_post_unauthorized(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostsCreateFormTests.group,
        }
        self.guest_client.post(reverse('posts:post_create'),
                                        data=form_data, )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_unauthorized(self):
        form_data = {
            'text': 'Test text',
            'group': PostsCreateFormTests.group,
        }
        self.guest_client.post(
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

    def test_edit_post_not_post_author(self):
        form_data = {
            'text': 'Test text111',
            'group': PostsCreateFormTests.group,
        }
        Post.objects.create(
            author=PostsCreateFormTests.post_author,
            group=PostsCreateFormTests.group,
            text='Test text'
        )
        self.authorized_client_2.post(
            reverse('posts:post_edit',
                    kwargs={'pk': self.post.id}), data=form_data,)
        var_for_resp = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response_2 = self.authorized_client_2.get(var_for_resp)
        form_fields = Post.objects.all()[:0]
        for value in form_fields:
            with self.subTest(value=value):
                response_2.context['post'][0].fields[value]
                self.assertNotEqual(form_fields, form_data)
