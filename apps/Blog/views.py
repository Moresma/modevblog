import math

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_POST

from django.db.models import Count, Q

from .models import Category, Post
from .forms import PostForm
from apps.comments.models import Comment


def with_counts(queryset):
    """Ajoute le nombre de likes et de commentaires à chaque article (pour les cartes)."""
    return queryset.annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count("comments", distinct=True),
    )


def login_required_json(request):
    """Réponse 401 avec l'adresse de connexion, utilisée par le JavaScript."""
    next_url = request.headers.get("x-next") or request.path
    return JsonResponse({"login_url": f"{reverse('login')}?next={next_url}"}, status=401)


def home(request):
    posts = with_counts(Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).select_related("author", "category"))

    return render(
        request,
        "Blog/home.html",
        {"posts": posts, "active_tab": "home"},
    )


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Articles de la catégorie et de ses sous-catégories.
    posts = with_counts(Post.objects.filter(
        Q(category=category) | Q(category__parent=category),
        status=Post.Status.PUBLISHED,
    ).select_related("author", "category"))

    return render(
        request,
        "Blog/category.html",
        {"category": category, "posts": posts, "active_tab": category.slug},
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author", "category"),
        id=post_id,
    )

    is_published = post.status == Post.Status.PUBLISHED
    can_manage = request.user.is_authenticated and (
        post.author == request.user or request.user.is_staff
    )

    # Un brouillon n'est visible que par son auteur ou un administrateur.
    if not is_published and not can_manage:
        raise Http404("Article introuvable.")

    # Commentaires avec leur nombre de likes.
    comments = post.comments.select_related("author").annotate(like_count=Count("likes"))

    # Ce que l'utilisateur connecté a déjà liké (pour colorer les cœurs).
    liked_post = False
    liked_comment_ids = set()
    if request.user.is_authenticated:
        liked_post = post.likes.filter(pk=request.user.pk).exists()
        liked_comment_ids = set(
            Comment.likes.through.objects.filter(
                user_id=request.user.pk, comment__post=post
            ).values_list("comment_id", flat=True)
        )

    # Temps de lecture estimé : environ 200 mots par minute.
    reading_time = max(1, math.ceil(len(post.content.split()) / 200))

    # Articles publiés, pour la navigation et les suggestions.
    published = Post.objects.filter(status=Post.Status.PUBLISHED)
    previous_post = next_post = None
    if post.published_at:
        previous_post = published.filter(published_at__lt=post.published_at).order_by("-published_at").first()
        next_post = published.filter(published_at__gt=post.published_at).order_by("published_at").first()

    # "À lire aussi" : 3 autres articles de la même rubrique.
    related_posts = with_counts(
        published.filter(category=post.category).exclude(pk=post.pk).select_related("author", "category")
    )[:3]

    return render(
        request,
        "Blog/post_detail.html",
        {
            "post": post,
            "reading_time": reading_time,
            "previous_post": previous_post,
            "next_post": next_post,
            "related_posts": related_posts,
            "author_post_count": published.filter(author=post.author).count(),
            "is_published": is_published,
            "can_manage": can_manage,
            "comments": comments,
            "comment_count": len(comments),
            "post_like_count": post.likes.count(),
            "liked_post": liked_post,
            "liked_comment_ids": liked_comment_ids,
        },
    )


@require_POST
def post_like(request, post_id):
    """Like / unlike d'un article (appelé en JavaScript, répond en JSON)."""
    if not request.user.is_authenticated:
        return login_required_json(request)

    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)      # déjà liké -> on retire
        liked = False
    else:
        post.likes.add(request.user)         # pas encore liké -> on ajoute
        liked = True

    return JsonResponse({"liked": liked, "count": post.likes.count()})


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            post = form.save(commit=False)

            post.author = request.user
            post.save()

            form.save_m2m()

            # Un article publié peut être consulté publiquement.
            if post.status == Post.Status.PUBLISHED:
                return redirect(
                    "post_detail",
                    post_id=post.id,
                )

            # Un brouillon reste dans "Mes articles".
            return redirect("my_posts")

    else:
        # Arrivée depuis le bouton d'une rubrique : on pré-sélectionne la catégorie.
        initial = {}
        category = Category.objects.filter(slug=request.GET.get("rubrique", "")).first()
        if category:
            initial["category"] = category.pk
        form = PostForm(initial=initial)

    return render(
        request,
        "Blog/post_form.html",
        {
            "form": form,
            "title": "Nouvel article",
        },
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )

    # Seul l'auteur ou un administrateur peut modifier.
    if post.author != request.user and not request.user.is_staff:
        raise Http404("Article introuvable.")

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            form.save()

            # Si l'article est publié,
            # retour vers sa page publique.
            if post.status == Post.Status.PUBLISHED:
                return redirect(
                    "post_detail",
                    post_id=post.id,
                )

            # Si l'article est un brouillon,
            # retour vers "Mes articles".
            return redirect("my_posts")

    else:
        form = PostForm(
            instance=post,
        )

    return render(
        request,
        "Blog/post_form.html",
        {
            "form": form,
            "title": "On peaufine ton article",
        },
    )


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )

    # Seul l'auteur ou un administrateur peut supprimer.
    if post.author != request.user and not request.user.is_staff:
        raise Http404("Article introuvable.")

    if request.method == "POST":
        post.delete()

        return redirect("home")

    return render(
        request,
        "Blog/post_confirm_delete.html",
        {
            "post": post,
        },
    )


@login_required
def my_posts(request):
    posts = Post.objects.filter(
        author=request.user
    ).select_related("category")

    # Compteurs affichés dans les filtres (Tous / Publiés / Brouillons).
    published_count = sum(1 for p in posts if p.status == Post.Status.PUBLISHED)

    return render(
        request,
        "Blog/my_posts.html",
        {
            "posts": posts,
            "published_count": published_count,
            "draft_count": len(posts) - published_count,
        },
    )

