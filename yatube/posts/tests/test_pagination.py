from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User
from posts.views import POSTS_PER_PAGE


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
        cls.post = Post.objects.bulk_create([
            Post(text='Тестовый текст',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_2',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_3',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_4',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_5',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_6',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_7',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_8',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_9',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_10',
                 author=cls.post_author,
                 group=cls.group,),
            Post(text='Тестовый текст_11',
                 author=cls.post_author,
                 group=cls.group,),
        ])

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
                self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
