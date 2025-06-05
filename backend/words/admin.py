from django.contrib import admin
from words import models

from django.contrib import admin
from words import models


@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "language")
    search_fields = ("word",)
    list_filter = ("language",)
    ordering = ("word",)
    filter_horizontal = ("synonyms",)  # This adds a nice UI for ManyToMany
