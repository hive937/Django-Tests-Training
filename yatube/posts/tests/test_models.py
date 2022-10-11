from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        field_str = {
            self.post.text[:15]: str(self.post),
            self.group.title: str(self.group),
        }
        for expected_object_name, expected in field_str.items():
            self.assertEqual(expected_object_name, expected)
