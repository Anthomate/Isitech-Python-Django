from django.urls import path
from . import views


urlpatterns = [
    ############################
    # Gestion des utilisateurs #
    ############################
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    #####################
    # Gestion des posts #
    #####################
    path('', views.post_list, name='post-list'),
    path('create/', views.post_create, name='post-create'),
    path('categories/', views.category_list, name='category-list'),
    path('categories/<slug:slug>/', views.category_detail, name='category-detail'),
    path('edit/<slug:slug>/', views.post_edit, name='post-edit'),
    path('delete/<slug:slug>/', views.post_delete, name='post-delete'),
    path('<slug:slug>/', views.post_detail, name='post-detail'),
]
