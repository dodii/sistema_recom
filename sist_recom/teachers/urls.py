from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("keywords_result/", views.keywords_result, name="keywords_result"),
    path("ranking_result/", views.ranking_result, name="ranking_result"),
]
