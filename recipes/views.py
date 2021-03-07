from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test, login_required
from foodgram.settings import ITEMS_FOR_PAGINATOR
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.utils.encoding import escape_uri_path

from .utils import food_time_filter, get_ingredients
from .forms import RecipeForm
from .models import Ingredients, Recipe, FollowRecipe, \
    FollowUser, IngredientRecipe, User, ShopingList


@user_passes_test(lambda u: u.is_superuser)
def add_ingredients(self):
    import json
    from django.http import HttpResponse

    with open('ingredients.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    for i in data:
        print('You added this new ingredient:', i)
        ingredient = Ingredients(title=i['title'], dimension=i['dimension'])
        ingredient.save()
    return HttpResponse('\n'.join(str(data)))


def index(request):
    recipe = Recipe.objects.select_related(
        'author').order_by('-pub_date').all()
    recipe_list, food_time = food_time_filter(request, recipe)

    paginator = Paginator(recipe_list, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    tags = ['breakfast', 'lunch', 'dinner']
    color = ['green', 'orange', 'purple']
    name = ['Завтрак', 'Обед', 'Ужин']
    result = list(zip(tags, name, color))
    return render(
        request, 'index.html', {
            'page': page,
            'paginator': paginator,
            'food_time': food_time,
            'result': result
        }
    )


def profile(request, username):
    recipe_author = get_object_or_404(User, username=username)

    recipe = Recipe.objects.select_related('author').filter(
        author=recipe_author).order_by('-pub_date').all()

    recipe_list, food_time = food_time_filter(request, recipe)
    paginator = Paginator(recipe_list, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'authorRecipe.html',
                  {
                      'page': page,
                      'paginator': paginator,
                      'username': recipe_author,
                      'food_time': food_time,
                  }
                  )


def recipe_view(request, recipe_id, username):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    username = get_object_or_404(User, username=username)
    ingredients = IngredientRecipe.objects.filter(recipe=recipe)
    return render(request, 'singlePage.html', {'username': username, 
                                                'recipe': recipe, 
                                                'ingredients': ingredients})


@login_required
def new_recipe(request):
    user = User.objects.get(username=request.user)

    if request.method == 'POST':
        ingr = get_ingredients(request)
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        if not ingr:
            form.add_error(None, 'Добавьте ингредиенты')

        elif form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = user
            recipe.save()
            for ingr_name, amount in ingr.items():
                ingr_obj = get_object_or_404(Ingredients, title=ingr_name)
                ingr_recipe = IngredientRecipe(
                    ingredient=ingr_obj,
                    recipe=recipe,
                    amount=amount,
                )
                ingr_recipe.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = RecipeForm()
    return render(request, 'formRecipe.html', {'form': form})


@login_required
def recipe_edit(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user != recipe.author:
        return redirect('index')

    if request.method == 'POST':
        form = RecipeForm(request.POST or None,
                          files=request.FILES or None, instance=recipe
                          )
        ingredients = get_ingredients(request)
        if form.is_valid():
            IngredientRecipe.objects.filter(recipe=recipe).delete()
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            for item in ingredients:
                IngredientRecipe.objects.create(
                    amount=ingredients[item],
                    ingredient=Ingredients.objects.get(title=f'{item}'),
                    recipe=recipe
                )
            form.save_m2m()
            return redirect('index')

    form = RecipeForm(request.POST or None,
                      files=request.FILES or None, instance=recipe)
                      

    return render(request, 'recipe_edit.html',
                  {'form': form, 'recipe': recipe, })


@login_required
def recipe_delete(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user

    if request.method == 'POST':
        author = get_object_or_404(User, username=username)
        if recipe.author == author == user or user.is_superuser:
            recipe.delete()
        return redirect('index')
    else:
        return render(request, 'recipe_delete.html', {
            'recipe_id': recipe_id,
            'username': username,
            'recipe': recipe,
        })


@login_required
def follow_index(request):
    follow = FollowUser.objects.filter(user=request.user)
    cnt = {}
    for author in follow:
        amount = Recipe.objects.filter(author=author.author).count()
        cnt[author.author] = amount
    paginator = Paginator(follow, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        "page": page,
        "paginator": paginator,
        "cnt": cnt,
    }
    )


@login_required
def favorite_index(request):
    recipe = Recipe.objects.select_related('author').filter(
        following_recipe__user__id=request.user.id)
    recipes, food_time = food_time_filter(request, recipe)
    paginator = Paginator(recipes, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'favorite.html', {
        'page': page,
        'paginator': paginator,
        'food_time': food_time,
    }
    )


@login_required
def shopping_list(request):
    shopping_list = ShopingList.objects.filter(user=request.user).all()
    return render(
        request,
        'shopping_list.html',
        {'shopping_list': shopping_list}
    )


@login_required
def download_card(request):
    recipes = Recipe.objects.filter(recipe_shoping_list__user=request.user)
    ingredients = recipes.values(
        'ingredients__title', 'ingredients__dimension'
    ).annotate(
        total_amount=Sum('recipe__amount')
    )
    file_data = ''
    for item in ingredients:
        line = ' '.join(str(value) for value in item.values())
        file_data += line + '\n'

    response = HttpResponse(
        file_data, content_type='application/text charset=utf-8'
    )
    myfile = 'Список покупок.txt'
    response['Content-Disposition'] = "attachment; filename="+ escape_uri_path(myfile)
    return response


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
