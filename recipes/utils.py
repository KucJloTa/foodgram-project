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
    food_time = request.GET.get('filter')

    if food_time in food:
        food[food_time] = (True,)

    queryset_new = queryset.filter(
        breakfast__in=food['breakfast'],
        lunch__in=food['lunch'],
        dinner__in=food['dinner'])

    return queryset_new, food_time
