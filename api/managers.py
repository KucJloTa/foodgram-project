from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


class PurchaseManager(models.Manager):
    def counter(self, user):
        try:
            return get_object_or_404(User, id=user).recipes.count()
        except ObjectDoesNotExist:
            return 0

    def get_purchases_list(self, user):
        try:
            return get_object_or_404(User, id=user).recipes.all()
        except ObjectDoesNotExist:
            return []

    def get_or_create_purchase(self, user):
        try:
            return get_object_or_404(User, id=user)
        except ObjectDoesNotExist:
            purchase = Purchase(user=user)
            purchase.save()
            return purchase
