from .models import POST
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

############################
# Gestion des utilisateurs #
############################

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Enregistrement réussi ! Bienvenue sur le blog.")
            return redirect('login')
        else:
            messages.error(request, "Erreur lors de l'enregistrement. Veuillez réessayer.")
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect('post-list')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

#####################
# Gestion des posts #
#####################

def post_list(request):
    posts = POST.objects.filter(status='published')
    for post in posts:
        if not post.slug:
            post.slug = 'slug-manquant'
            post.save()
    return render(request, 'blog/home.html', {'posts': posts})

def post_detail(request, slug):
    try:
        post = POST.objects.get(slug=slug, status='published')
    except POST.DoesNotExist:
        raise Http404("L'article demandé n'existe pas.")
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Votre article a été créé avec succès.")
            return redirect('post-list')
        else:
            messages.error(request, "Erreur lors de la création de l'article. Veuillez vérifier le formulaire.")
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('post-list')

@login_required
def post_edit(request, slug):
    post = POST.objects.get(slug=slug)

    if post.author != request.user:
        messages.error(request, "Vous n'êtes pas l'auteur de cet article.")
        return redirect('post-detail', slug=slug)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre article a été modifié avec succès.")
            return redirect('post-detail', slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {'form': form})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(POST, slug=slug)

    if post.author != request.user:
        messages.error(request, "Vous n'êtes pas l'auteur de cet article.")
        return redirect('post-detail', slug=slug)

    post.delete()
    messages.success(request, "L'article a été supprimé avec succès.")
    return redirect('post-list')
