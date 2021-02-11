from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from taggit.models import Tag

from api.models import Purchase, Subscription
from foodgram.settings import ITEMS_FOR_PAGINATOR

from .forms import RecipeForm
from .models import IngredientForRecipe, Recipe, User
from .utils import get_tags, save_recipe, get_ingredients


def index(request):
    """
    Отображает самые последние рецепты с тегами 6 шт на странице
    """
    recipes = Recipe.objects.all()
    tags_qs, tags_from_get = get_tags(request)
# "Фильтрация по рецептов по тэгам повторяется между вьюхами - давай оформим отдельной функцией"
# - не понял, фильтр же разный, зачем выносить в отдельную вьюху? не очень понял этот момент, а главное как?))
    if tags_qs:
        recipes = Recipe.objects.filter(tags__slug__in=tags_qs).distinct()

#    tag_recipe_filter(tags_qs)

    paginator = Paginator(recipes, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'recipes/index.html',
        {'recipes': recipes, 'paginator': paginator,
         'page': page, 'tags': tags_from_get}
    )


@login_required
def new_recipe(request):
    """
    GET: Отобразит форму для нового рецепта

    POST: Если форма валидная сохранит рецепт в базу, если нет покажет ошибки
    """
    form = RecipeForm(request.POST or None, files=request.FILES or None)
#"В нескольких вьюхах в контекст шаблона отдаются все тэги - можно оформить кастомным темплейт фильтром или контекст процессором"
#Расскажи пжл поподробнее свою логику)
    tags = Tag.objects.all()

    if form.is_valid():
        ingredients = get_ingredients(request.POST)
        save_recipe(recipe, ingredients, request)
        return redirect('index')
    return render(request, 'recipes/formRecipe.html', {'form': form, 'tags': tags})


@login_required
def recipe_edit(request, recipe_id, username):
    """
    GET: Отобразит форму для редактирования существующих рецептов

    POST: Проверит форму и сохранит рецепт, если не валидна выдаст ошибку
    """
    recipe = get_object_or_404(Recipe, author__username=username, id=recipe_id)
    ing = IngredientForRecipe.objects.filter(recipe=recipe_id)
    form = RecipeForm(request.POST or None, files=request.FILES or None,
                      instance=recipe)
    tags = Tag.objects.all()
    context = {'form': form, 'recipe': recipe,
               'ingredients': ing, 'tags': tags}

    if recipe.author == request.user:
        ingredients = get_ingredients(request.POST)

        if form.is_valid():
            ing.delete()
            recipe = form.save(commit=False)
            save_recipe(recipe, ingredients, request)
            return redirect('recipe', username=request.user.username,
                            recipe_id=recipe.id)

        return render(request, 'recipes/formRecipe.html', context)
    else:
        return redirect('recipe', username=request.user.username,
                        recipe_id=recipe.id)


@login_required
def recipe_delete(request, recipe_id, username):
    """
    Удаляет рецепт
    """
    recipe = get_object_or_404(Recipe, author__username=username, id=recipe_id)

    if request.user != recipe.author:
        return redirect(
            'recipe_view',
            username=username,
            recipe_id=recipe_id
        )

    recipe.delete()
    return redirect('index')


def recipe_view(request, username, recipe_id):
    """
    Отображает страницу рецепта
    """
    recipe = get_object_or_404(Recipe, author__username=username, id=recipe_id)
    ingredients = recipe.recipeingredient.all()
    return render(request, 'recipes/recipe_view.html', {'recipe': recipe,
                                                        'ingredients': ingredients})


def profile(request, username):
    """
    Отображает все рецепты данного юзера, отфильтрованного по тегам,
    6 шт на странице
    """
    author = get_object_or_404(User, username=username)
    recipes = Recipe.objects.filter(author=author)
    tags_qs, tags_from_get = get_tags(request)

    if tags_qs:
        recipes = Recipe.objects.filter(
            author=author,
            tags__slug__in=tags_qs).distinct()

    paginator = Paginator(recipes, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/index.html',
                  {'author': author, 'page': page,
                   'paginator': paginator, 'tags': tags_from_get}
                  )


@login_required
def subscriptions(request, username):
    """
    Отображает всех юзеров на кого подписан автор
    """
    user = get_object_or_404(User, username=username)
    subscriptions = User.objects.prefetch_related('recipes').filter(
        following__user=user.id)
    paginator = Paginator(subscriptions, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'recipes/myFollow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def favorites(request, username):
    """
    Отображает все рецепты которые автор добавил в избранное
    """
    user = get_object_or_404(User, username=username)
    recipes = Recipe.objects.filter(favourites__user=request.user)
    tags_qs, tags_from_get = get_tags(request)

    if tags_qs:
        recipes = Recipe.objects.filter(favourites__user=request.user,
                                        tags__slug__in=tags_qs).distinct()

    paginator = Paginator(recipes, ITEMS_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/index.html', {
        'recipes': recipes, 'paginator': paginator, 'page': page,
        'username': user, 'tags': tags_from_get
    })


@login_required
def purchases_list(request):
    """
    Отображает список покупок
    """
    recipes_list = Purchase.purchase.get_purchases_list(request.user)
    return render(request,
                  'recipes/shopList.html',
                  {'recipes_list': recipes_list}
                  )


@login_required
def download_shoplist(request):
    """
    Скачивает список покупок
    """
    user = request.user
    filename = f'{user.username}_list.txt'
    recipes = Purchase.purchase.get_purchases_list(user).values(
        'ingredients__name', 'ingredients__unit'
    )
    ingredients = recipes.annotate(Sum('recipeingredient__amount')).order_by()
    products = [
        (f'{i["ingredients__name"]} -'
         f' {i["recipeingredient__amount__sum"]} {i["ingredients__unit"]}')
        for i in ingredients]
    content = '\n'.join(products)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
