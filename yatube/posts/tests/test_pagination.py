from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
from posts.views import POSTS_PER_PAGE


class PaginatorViewsTest(TestCase):

    def without_bulk(self):
        for i in range(12):
            Post.objects.bulk_create([
                Post(text=f'Тестовый текст {i}',
                     author=cls.post_author,
                     group=cls.group, ),
            ])

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
        cls.post = without_bulk()

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contain_ten_records(self):
        pages_name = {
            'posts/index.html/': reverse('posts:index'),
            'posts/group_list.html/': reverse('posts:group_list',
                                              kwargs={'slug': 'test-slug'}),
            'posts/profile.html/':
                reverse('posts:profile',
                        kwargs={'username': self.post_author}),
        }

        for value, address in pages_name.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(address)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_PER_PAGE)
