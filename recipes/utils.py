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
        'breakfast': (),
        'lunch': (),
        'dinner': ()
    }
    food_time = request.GET.getlist('filters')
    for i in food_time:
        if i in food:
            food[i] = (True,)

    if food_time:
        queryset_new = queryset.filter(
            Q(breakfast__in=food['breakfast']) |
            Q(lunch__in=food['lunch']) |
            Q(dinner__in=food['dinner'])).distinct()
        return queryset_new, food_time
    else:
        queryset_new = queryset
        return queryset_new, food_time