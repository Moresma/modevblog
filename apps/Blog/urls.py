from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),

    path(
        "categorie/<slug:slug>/", views.category_posts, name="category",
    ),

    path(
        "post/<int:post_id>/", views.post_detail, name="post_detail",
    ),

    path(
        "post/create/", views.post_create, name="post_create",
    ),

    path(
        "post/<int:post_id>/like/", views.post_like, name="post_like",
    ),

    path(
        "mes-articles/", views.my_posts, name="my_posts"
        ),

    path(
        "post/<int:post_id>/edit/", views.post_edit, name="post_edit",
    ),

    path(
        "post/<int:post_id>/delete/", views.post_delete, name="post_delete",
    ),
]