from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required

POSTS_PER_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    title = group.title
    group_post_list = Post.objects.filter(group=group).all()
    paginator = Paginator(group_post_list, POSTS_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=username)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    username = request.user.username
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        post_create = form.save(commit=False)
        post_create.author = request.user
        post_create.save()
        return redirect('posts:profile', username)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, pk):
    template = 'posts/create_post.html'
    edit_post = get_object_or_404(Post, id=pk)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', pk)
    form = PostForm(request.POST or None, instance=edit_post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk)
    context = {
        'form': form,
        'is_edit': True,
        "post_id": pk,
    }
    return render(request, template, context)
