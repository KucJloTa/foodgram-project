from taggit.models import Tag

from .models import Ingredient, IngredientForRecipe


def get_tags(request):
    tags_lst = []
    if 'tags' in request.GET:
        tags_lst = request.GET.get('tags')
        _ = tags_lst.split(',')
        tags_query = Tag.objects.filter(slug__in=_).values('slug')
    else:
        tags_query = False
    return [tags_query, tags_lst]


def get_ingredients(data):
    ingredient_num = set()
    ingredients = []
    for key in data:
        if key.startswith('nameIngredient_'):
            _, number = key.split('_')
            ingredient_num.add(number)
    for number in ingredient_num:
        ingredients.append(
            {
                'name': data[f'nameIngredient_{number}'],
                'unit': data[f'unitsIngredient_{number}'],
                'amount': float(data[f'valueIngredient_{number}']),
            }
        )
    return ingredients


def save_recipe(recipe, ingredients, request):
    recipe.author = request.user
    recipe.save()
    recipe_ingredients = []

    for item in ingredients:
        recipe_ing = IngredientForRecipe(
            amount=item.get('amount'),
            ingredient=Ingredient.objects.get(name=item.get('name')),
            recipe=recipe)
        recipe_ing.save()
