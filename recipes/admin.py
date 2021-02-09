from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'dimension')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'cooking_time',
        'pub_date'
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'quantity')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'color')
