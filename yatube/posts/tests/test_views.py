from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

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
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            '/posts/index.html/': reverse('posts:index'),
            f'posts/group_list.html': reverse(f'posts:{self.group.slug}'),
            f'posts/profile.html': reverse(f'posts:{self.post.author}'),
            f'posts/post_detail.html': reverse(f'posts:{self.post.pk}', kwargs={'slug': 'test-slug'}),
        }
        for address, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_post_uses_correct_template(self):
        response = self.authorized_client.get(reverse('posts:post_edit'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_post_uses_correct_template(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_list = Post.objects.all()
        paginator = Paginator(post_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        form_fields = {
            'page_obj': page_obj,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group_list'))
        group = get_object_or_404(Group, slug=slug)
        group_post_list = Post.objects.filter(group=group).all()
        paginator = Paginator(group_post_list, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        form_fields = {
            'title': forms.fields.CharField,
            'group': group,
            'page_obj': page_obj,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:profile'))
        posts = Post.objects.filter(author__username=username)
        paginator = Paginator(posts, POSTS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        form_fields = {
            'author': forms.fields.CharField,
            'posts': posts,
            'page_obj': page_obj,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail'))
        post = get_object_or_404(Post, id=post_id)
        form_fields = {
            "post": post,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:create_post'))
        username = request.user.username
        form = PostForm(request.POST or None)
        if form.is_valid():
            post_create = form.save(commit=False)
            post_create.author = request.user
            post_create.save()
            return redirect('posts:profile', username)
        form_fields = {
            'form': form,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit'))
        edit_post = get_object_or_404(Post, id=pk)
        if request.user != edit_post.author:
            return redirect('posts:post_detail', pk)
        form = PostForm(request.POST or None, instance=edit_post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', pk)
        form_fields = {
            'form': form,
            'is_edit': True,
            "post_id": pk,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_on_pages(self):
        pages_names = {
            reverse('posts:index'): f'{self.post.pk}',
            reverse(f'posts:post_detail'): f'{self.post.pk}',
            reverse(f'posts:profile'): f'{self.post.pk}',
        }

        for reverse_name, post_info in pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIsInstance(response.context.get('page').object_list, post_info)

    def test_post_not_in_wrong_group(self):
        response = self.authorized_client.get(reverse(f'posts:{self.group_2.slug}'))
        self.assertIsInstance(response.context.get(f'{self.post.pk}').object_list, post_info)


class PaginatorViewsTest(TestCase):
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
            '/posts/index.html/': 'object_list',
            '/posts/group_list.html/': 'object_list',
            '/posts/profile.html/': 'object_list',
        }

        for value, expected in pages_name.items():
            with self.subTest(value=value):
                response = self.client.get(reverse(value))
                self.assertEqual(len(response.context[expected]), 10)

