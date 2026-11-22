from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.Blog.models import Post

from .forms import CommentForm
from .models import Comment


def _is_ajax(request):
    """Vrai si la requête vient du JavaScript de la page (fetch)."""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def _login_response(request, post_id):
    """Visiteur non connecté : JSON 401 pour le JS, sinon redirection vers la connexion."""
    next_url = reverse("post_detail", args=[post_id]) + "#commentaires"
    login_url = f"{reverse('login')}?next={next_url}"
    if _is_ajax(request):
        return JsonResponse({"login_url": login_url}, status=401)
    return redirect(login_url)


@require_POST
def add_comment(request, post_id):
    # On ne commente que les articles publiés.
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    if not request.user.is_authenticated:
        return _login_response(request, post.id)

    form = CommentForm(request.POST)

    if not form.is_valid():
        if _is_ajax(request):
            return JsonResponse({"error": "Ton commentaire est vide !"}, status=400)
        return redirect("post_detail", post_id=post.id)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()

    if _is_ajax(request):
        # Renvoie le HTML du nouveau commentaire, que le JS ajoute en haut de la liste.
        html = render_to_string(
            "comments/_comment.html",
            {"comment": comment},
            request=request,
        )
        return JsonResponse({"html": html, "count": post.comments.count()})

    return redirect(reverse("post_detail", args=[post.id]) + "#commentaires")


@require_POST
def comment_like(request, comment_id):
    """Like / unlike d'un commentaire (appelé en JavaScript, répond en JSON)."""
    comment = get_object_or_404(Comment, id=comment_id, post__status=Post.Status.PUBLISHED)

    if not request.user.is_authenticated:
        return _login_response(request, comment.post_id)

    if comment.likes.filter(pk=request.user.pk).exists():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "count": comment.likes.count()})
