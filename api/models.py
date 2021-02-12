from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from recipes.models import Recipe
from .managers import PurchaseManager

User = get_user_model()


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favourites')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favourites')


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'подсписка'
        verbose_name_plural = 'подписки'
        constraints = [
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique subscription',
        )
    ]


class Purchase(models.Model):
    recipes = models.ManyToManyField(
        Recipe, related_name='purchases')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='purchases')
    purchase = PurchaseManager()

    class Meta:
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'
