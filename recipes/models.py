from django.db import models
from django.contrib.auth import get_user_model
from sorl.thumbnail import ImageField

User = get_user_model()


class Ingredients(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    dimension = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.title} {self.dimension}'


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name='recipe')
    ingredient = models.ForeignKey(
        "Ingredients",
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingredient.title} {self.amount} {self.ingredient.dimension}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(
        "Ingredients",
        related_name='recipes',
        through='IngredientRecipe'
    )
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True)

    breakfast = models.BooleanField(
        default=False, verbose_name='Завтрак'
    )
    lunch = models.BooleanField(
        default=False, verbose_name='Обед'
    )
    dinner = models.BooleanField(
        default=False, verbose_name='Ужин'
    )

    def __str__(self):
        return self.title


class FollowRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_recipe')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='following_recipe')

    def __str__(self):
        return f'follower - {self.user} following recipe - {self.recipe}'


class FollowUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        unique_together = ['user', 'author']

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'


class ShopingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shoping_list')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shoping_list')
