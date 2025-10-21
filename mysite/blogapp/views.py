from django.contrib.gis.feeds import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy
from .models import Article, ArticleNews


class ArticleNewsListView(ListView):
    queryset = ArticleNews.objects.filter(published_at__isnull=False).order_by(
        "-published_at"
    )


class ArticleNewsDetailView(DetailView):
    context_object_name = "article"
    model = ArticleNews


class LatestArticlesListFeed(Feed):
    title = "Blog articles latest"
    description = "Updates on changes and additions blog articles"
    link = reverse_lazy("blogapp:article-news")

    def items(self):
        return ArticleNews.objects.order_by("-published_at")[:5]

    def item_title(self, item: ArticleNews):
        return item.title

    def item_description(self, item: ArticleNews):
        return item.body[:200]


class ArticleListView(ListView):
    """
    Класс для вывода всех постов на стену
    """

    model = Article
    template_name = "blogapp/article-list.html"
    context_object_name = "articles"
    ordering = ["-pub_date"]

    def get_queryset(self):
        return (
            Article.objects.select_related(
                "author", "category"
            )  # подгружаем author и category
            .prefetch_related("tags")  # подгружаем теги
            .defer("content")  # исключаем поле content из выборки
            .all()
        )


class ArticleDetailView(DetailView):
    """
    Класс для отображения деталей поста
    """

    model = Article
    template_name = "blogapp/article-detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.select_related("author", "category").prefetch_related(
            "tags"
        )
