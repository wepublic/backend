from django.contrib import admin
from wp_news.models import NewsEntry
# Register your models here.
from django.db import models
from pagedown.widgets import AdminPagedownWidget


class NewsEntryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget},
    }


admin.site.register(NewsEntry, NewsEntryAdmin)
