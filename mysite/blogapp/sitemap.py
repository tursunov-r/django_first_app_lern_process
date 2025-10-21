from django.contrib.sitemaps import Sitemap
from .models import ArticleNews


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return ArticleNews.objects.filter(published_at__isnull=False).order_by(
            "-published_at"
        )

    def lastmod(self, object: ArticleNews):
        return object.published_at
