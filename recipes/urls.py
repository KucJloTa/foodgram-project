from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_ingredients, name='add_ingredients'),
    path('new/', views.new_recipe, name='new_recipe'),
    path('follow/', views.follow_index, name='follow'),
    path('favorite/', views.favorite_index, name='favorite'),
    path('shopping-list/', views.shopping_list, name='shopping-list'),
    path('download_card/', views.download_card, name='download_card'),
    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:recipe_id>/', views.recipe_view, 
        name='recipe_view'),
    path('<username>/<int:recipe_id>/edit/', views.recipe_edit, 
        name='recipe_edit'),
    path('<username>/<int:recipe_id>/delete/', views.recipe_delete, 
        name='recipe_delete'),
]