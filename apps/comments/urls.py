from django.urls import path
from .import views
app_name = "comments"

urlpatterns = [
    path("post/<int:post_id>/add/", views.add_comment, name= "add_comment", ),
    path("<int:comment_id>/like/", views.comment_like, name="comment_like"),
]