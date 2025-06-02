from django.contrib import admin
from words import models


@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "language", "difficulty")
    search_fields = ("word",)
    list_filter = ("language",)
    ordering = ("word",)


@admin.register(models.Synonym)
class SynonymAdmin(admin.ModelAdmin):
    list_display = ("word", "synonym")
    search_fields = ("word__word", "synonym__word")
    list_filter = ("word__language", "synonym__language")
    ordering = ("word__word", "synonym__word")
