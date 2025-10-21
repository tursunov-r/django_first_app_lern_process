from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleNewsListView,
    ArticleNewsDetailView,
    LatestArticlesListFeed,
)


app_name = "blogapp"


urlpatterns = [
    path("list/", ArticleListView.as_view(), name="article-list"),
    path("detail/<int:pk>", ArticleDetailView.as_view(), name="article-detail"),
    path("news/", ArticleNewsListView.as_view(), name="article-news"),
    path(
        "news/<int:pk>/detail/",
        ArticleNewsDetailView.as_view(),
        name="article-news-detail",
    ),
    path("news/latest/feed/", LatestArticlesListFeed(), name="article-news-latest"),
]
