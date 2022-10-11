from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group')
        verbose_name = 'Форма поста'
        verbose_name_plural = 'Формы постов'
        help_texts = {
            'name': ('Это форма создания поста'),
        }
