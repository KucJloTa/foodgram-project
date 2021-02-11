from taggit.models import Tag

from .models import Ingredient, IngredientForRecipe, Recipe


def get_tags(request):
    tags_from_get = []
    if 'tags' in request.GET:
        tags_from_get = request.GET.get('tags')
        sl_tag = tags_from_get.split(',')
        tags_qs = Tag.objects.filter(slug__in=sl_tag).values('slug')
    else:
        tags_qs = False
    return [tags_qs, tags_from_get]


# def tag_recipe_filter(tags_qs):
#     if tags_qs:
#         recipes = Recipe.objects.filter(tags__slug__in=tags_qs).distinct()
#         return recipes


def get_ingredients(data):
    ingredient_numbers = set()
    ingredients = []
    for key in data:
        if key.startswith('nameIngredient_'):
            _, number = key.split('_')
            ingredient_numbers.add(number)
    for number in ingredient_numbers:
        ingredients.append(
            {
                'name': data[f'nameIngredient_{number}'],
                'unit': data[f'unitsIngredient_{number}'],
                'amount': float(data[f'valueIngredient_{number}']),
            }
        )
    return ingredients


def save_recipe(recipe, ingredients, request):
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    recipe_ingredients = []

    for item in ingredients:
        recipe_ing = IngredientForRecipe(
            amount=item.get('amount'),
            ingredient=Ingredient.objects.get(name=item.get('name')),
            recipe=recipe)
        recipe_ing.save()
    form.save_m2m()
