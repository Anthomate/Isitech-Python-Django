import logging

from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import POST, Category
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

# Configuration des loggers
logger = logging.getLogger(__name__)
auth_logger = logging.getLogger('authentication')


############################
# Gestion des utilisateurs #
############################

@login_required
@csrf_exempt
def toggle_favorite(request, post_id):
    try:
        post = get_object_or_404(POST, id=post_id)
        if request.user in post.favorited_by.all():
            post.favorited_by.remove(request.user)
            is_favorited = False
        else:
            post.favorited_by.add(request.user)
            is_favorited = True
        return JsonResponse({'is_favorited': is_favorited, 'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False})

def register(request):
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                auth_logger.info(f"Nouvel utilisateur enregistré : {user.username}")
                messages.success(request, "Enregistrement réussi ! Bienvenue sur le blog.")
                return redirect('login')
            else:
                auth_logger.warning(f"Échec d'enregistrement : {form.errors}")
                messages.error(request, "Erreur lors de l'enregistrement. Veuillez réessayer.")
        else:
            form = UserCreationForm()
        return render(request, 'blog/register.html', {'form': form})
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur inattendue s'est produite.")
        return redirect('register')


def user_login(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                auth_logger.info(f"Connexion réussie : {user.username}")
                messages.success(request, "Connexion réussie !")
                return redirect('post-list')
            else:
                auth_logger.warning(f"Échec de connexion - Erreurs de formulaire : {form.errors}")
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            form = AuthenticationForm()
        return render(request, 'blog/login.html', {'form': form})
    except Exception as e:
        logger.error(f"Erreur lors de la connexion : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur inattendue s'est produite lors de la connexion.")
        return redirect('login')


def user_logout(request):
    try:
        username = request.user.username if request.user.is_authenticated else "Utilisateur non authentifié"
        logout(request)
        auth_logger.info(f"Déconnexion réussie : {username}")
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return redirect('post-list')
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur est survenue lors de la déconnexion.")
        return redirect('post-list')


#####################
# Gestion des posts #
#####################

def post_list(request):
    try:
        # Récupération des catégories
        categories = Category.objects.all()

        # Filtrer les posts publiés
        posts = POST.objects.filter(status='published')

        # Filtrage par catégorie
        selected_category = request.GET.get('category')
        if selected_category:
            posts = posts.filter(category__slug=selected_category)

        # Filtrage par favoris si l'utilisateur est connecté et choisit cette option
        show_favorites = request.GET.get('favorites') == 'true'
        if show_favorites and request.user.is_authenticated:
            posts = posts.filter(favorited_by=request.user)

        return render(request, 'blog/home.html', {
            'posts': posts,
            'categories': categories,
            'selected_category': selected_category,
            'show_favorites': show_favorites
        })
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la liste des posts : {str(e)}", exc_info=True)
        messages.error(request, "Impossible de charger la liste des articles.")
        return render(request, 'blog/home.html', {'posts': [], 'categories': []})



def post_detail(request, slug):
    try:
        post = POST.objects.get(slug=slug, status='published')
        logger.info(
            f"Article consulté : {post.title} par {request.user.username if request.user.is_authenticated else 'anonyme'}")
        return render(request, 'blog/post_detail.html', {'post': post})
    except POST.DoesNotExist:
        logger.warning(f"Tentative d'accès à un article inexistant : {slug}")
        messages.error(request, "L'article que vous cherchez n'existe pas.")
        raise Http404("L'article demandé n'existe pas.")
    except Exception as e:
        logger.error(f"Erreur lors de la consultation de l'article {slug} : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur est survenue lors de la consultation de l'article.")
        return redirect('post-list')


@login_required
def post_create(request):
    logger.info(f"Tentative de création de post par {request.user.username}")
    try:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                logger.info(f"Post créé avec succès : {post.title}")
                messages.success(request, "Votre article a été créé avec succès.")
                return render(request, 'blog/post_form.html', {'form': form})
            else:
                logger.warning(f"Échec de création de post : {form.errors}")
                messages.error(request, "Erreur lors de la création de l'article. Veuillez vérifier le formulaire.")
        else:
            form = PostForm()
        return render(request, 'blog/post_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Erreur lors de la création de post : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur inattendue s'est produite.")
        return redirect('post-create')


@login_required
def post_edit(request, slug):
    try:
        post = POST.objects.get(slug=slug)

        if post.author != request.user:
            logger.warning(f"Tentative d'édition non autorisée de l'article {slug} par {request.user.username}")
            messages.error(request, "Vous n'êtes pas l'auteur de cet article.")
            return redirect('post-detail', slug=slug)

        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                logger.info(f"Article modifié avec succès : {post.title} par {request.user.username}")
                messages.success(request, "Votre article a été modifié avec succès.")
                return redirect('post-detail', slug=post.slug)
            else:
                logger.warning(f"Échec de modification de l'article : {form.errors}")
                messages.error(request, "Erreur lors de la modification de l'article.")
        else:
            form = PostForm(instance=post)

        return render(request, 'blog/post_form.html', {'form': form})
    except POST.DoesNotExist:
        logger.error(f"Tentative d'édition d'un article inexistant : {slug}")
        messages.error(request, "L'article recherché n'existe pas.")
        return redirect('post-list')
    except Exception as e:
        logger.error(f"Erreur lors de l'édition de l'article {slug} : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur inattendue s'est produite.")
        return redirect('post-list')


@login_required
def post_delete(request, slug):
    try:
        post = get_object_or_404(POST, slug=slug)

        if post.author != request.user:
            logger.warning(f"Tentative de suppression non autorisée de l'article {slug} par {request.user.username}")
            messages.error(request, "Vous n'êtes pas l'auteur de cet article.")
            return redirect('post-detail', slug=slug)

        post_title = post.title  # Sauvegarde du titre avant suppression
        post.delete()

        logger.info(f"Article supprimé : {post_title} par {request.user.username}")
        messages.success(request, "L'article a été supprimé avec succès.")
        return redirect('post-list')
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'article {slug} : {str(e)}", exc_info=True)
        messages.error(request, "Une erreur est survenue lors de la suppression de l'article.")
        return redirect('post-list')

def category_list(request):
    categories = Category.objects.annotate(article_count=Count('post')).order_by('name')
    return render(request, 'blog/category_list.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.post.filter(status='published').order_by('-created_at')
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts,
    })