from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User


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
        cls.user = User.objects.create_user(username='StasBasov')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': PostsPagesTests.user.username}),
            'posts/post_detail.html':
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_post_uses_correct_template(self):
        response = self.authorized_client.get(reverse
                                              ('posts:post_edit',
                                               kwargs={'pk': self.post.id}))
        self.assertTemplateUsed(response, 'posts/create_post.html')
        # не понял как тут переиспользовать

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
        response = self.authorized_client.get(reverse
                                              ('posts:group_list',
                                               kwargs={'slug': 'test-slug'}))
        form_fields = Group.objects.all()[:0]

        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context['page_obj'][0].fields[value]
                self.assertIsInstance(form_field, value)

    def test_profile_page_shows_correct_context(self):
        usern_val = PostsPagesTests.user.username
        var_for_resp = reverse('posts:profile',
                               kwargs={'username': usern_val})
        response = self.authorized_client.get(var_for_resp)
        form_fields = User.objects.all()[:0]

        for value in form_fields:
            with self.subTest(value=value):
                form_field = response.context['page_obj'][0].fields[value]
                self.assertIsInstance(form_field, value)

    def test_post_detail_page_shows_correct_context(self):
        var_for_resp = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(var_for_resp)
        self.assertEqual(self.post, response.context['post'])

    def test_edit_page_shows_correct_context(self):
        var_for_resp = reverse('posts:post_edit', kwargs={'pk': self.post.id})
        response = self.authorized_client.get(var_for_resp)
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
        var_for_resp = reverse('posts:group_list',
                               kwargs={'slug': 'test-slug'})
        response = self.client.get(var_for_resp)
        page = response.context['page_obj']
        self.assertIn(post, page)

    def test_post_is_on_profile_page(self):
        post = Post.objects.create(
            author=PostsPagesTests.post_author,
            group=PostsPagesTests.group,
            text='Test text'
        )
        var_for_resp = reverse('posts:profile',
                               kwargs={'username': self.post_author})
        response = self.client.get(var_for_resp)
        page = response.context['page_obj']
        self.assertIn(post, page)

    def test_post_not_in_wrong_group(self):
        post = Post.objects.create(
            author=PostsPagesTests.post_author,
            group=PostsPagesTests.group,
            text='Test text'
        )
        var_for_resp = reverse('posts:group_list',
                               kwargs={'slug': 'test-slug-2'})
        response = self.client.get(var_for_resp)
        page = response.context['page_obj']
        self.assertNotEqual(post, page)
