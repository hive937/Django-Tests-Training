from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
        )
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_urls_uses_correct_template_at_desired_location(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)

    def test_create_url_exists_at_desired_location_unauthorized(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_exists_at_desired_location_unauthorized(self):
        response = self.guest_client.get(f'/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 404)

    def test_create_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location(self):
        response = self.authorized_client.get(f'/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 404)
