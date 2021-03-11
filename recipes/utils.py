from django.db.models import Q


def get_ingredients(request):
    ingredients = {}
    for key in dict(request.POST.items()):
        if 'nameIngredient' in key:
            a = key.split('_')
            ingredients[dict(request.POST.items())[key]] = int(request.POST[
                f'valueIngredient_{a[1]}'])

    return ingredients


def food_time_filter(request, queryset):
    food = {
        'breakfast': (True, False),
        'lunch': (True, False),
        'dinner': (True, False)
    }
    food_time = request.GET.getlist('filters')
    for i in food_time:
        if i in food:
            food[i] = (True,)

    queryset_new = queryset.filter(Q(breakfast__in=food['breakfast']) | Q(lunch__in=food['lunch']) | Q(dinner__in=food['dinner'])).distinct()

    return queryset_new, food_time
