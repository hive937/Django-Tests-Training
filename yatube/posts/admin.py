from django.contrib import admin

from .models import Post, Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('text', 'group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
