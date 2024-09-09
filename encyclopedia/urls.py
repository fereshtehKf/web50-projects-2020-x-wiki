from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("edit/<str:entry>", views.edit, name="edit"),
    path("wiki/<str:entry>", views.wiki, name="wiki"),
    path("new", views.new, name="new"),
    path("search/", views.search, name="search"),
  path("random", views.random_entry, name="random_entry"),

]

handler404 = "encyclopedia.views.handler404"