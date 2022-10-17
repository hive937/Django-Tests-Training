from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
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
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(f'posts:group_list', kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': self.user.username}),
            'posts/post_detail.html': (reverse('posts:post_detail', kwargs={'post_id': self.post.id})),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_post_uses_correct_template(self):
        response = self.authorized_client.get(reverse(f'posts:post_edit', kwargs={'pk': self.post.id}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_post_uses_correct_template(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        form_fields = Post.objects.all()[:0]

        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context['page_obj'][0].fields[value]
                self.assertIsInstance(form_field, value)

    def test_group_list_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        form_fields = Group.objects.all()[:0]

        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context['page_obj'][0].fields[value]
                self.assertIsInstance(form_field, value)

    def test_profile_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': self.user.username}))
        form_fields = User.objects.all()[:0]

        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context['page_obj'][0].fields[value]
                self.assertIsInstance(form_field, value)

    def test_post_detail_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        form_fields = list(Post.objects.all()[:0])

        self.assertEqual(self.post, response.context['post'])

    def test_edit_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'pk': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for key, value in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[key]
                self.assertIsInstance(form_field, value)

    def test_post_is_on_index_page(self):
        post = Post.objects.create(
            author=PostsPagesTests.post_author,
            group=PostsPagesTests.group,
            text='Test text'
        )
        response = self.client.get(reverse('posts:index'))
        page = response.context['page_obj']
        self.assertIn(post, page)

    def test_post_is_on_group_page(self):
        post = Post.objects.create(
            author=PostsPagesTests.post_author,
            group=PostsPagesTests.group,
            text='Test text'
        )
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        page = response.context['page_obj']
        self.assertIn(post, page)

    def test_post_is_on_profile_page(self):
        post = Post.objects.create(
            author=PostsPagesTests.post_author,
            group=PostsPagesTests.group,
            text='Test text'
        )
        response = self.client.get(reverse('posts:profile', kwargs={'username': self.post_author}))
        page = response.context['page_obj']
        self.assertIn(post, page)

    def test_post_not_in_wrong_group(self):
        post = Post.objects.create(
            author=PostsPagesTests.post_author,
            group=PostsPagesTests.group,
            text='Test text'
        )
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug-2'}))
        page = response.context['page_obj']
        self.assertNotEqual(post, page)

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            text='Тестовый текст_2',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_3 = Post.objects.create(
            text='Тестовый текст_3',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_4 = Post.objects.create(
            text='Тестовый текст_4',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_5 = Post.objects.create(
            text='Тестовый текст_5',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_6 = Post.objects.create(
            text='Тестовый текст_6',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_7 = Post.objects.create(
            text='Тестовый текст_7',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_8 = Post.objects.create(
            text='Тестовый текст_8',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_9 = Post.objects.create(
            text='Тестовый текст_9',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_10 = Post.objects.create(
            text='Тестовый текст_10',
            author=cls.post_author,
            group=cls.group,
        )
        cls.post_11 = Post.objects.create(
            text='Тестовый текст_11',
            author=cls.post_author,
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contain_ten_records(self):
        pages_name = {
            'posts/index.html/': reverse('posts:index'),
            'posts/group_list.html/': reverse(f'posts:group_list', kwargs={'slug': 'test-slug'}),
            'posts/profile.html/': reverse('posts:profile', kwargs={'username': self.post_author}),
        }

        for value, address in pages_name.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(address)
                self.assertEqual(len(response.context['page_obj']), 10)


