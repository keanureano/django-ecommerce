from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    starting_price = models.FloatField()
    image_url = models.CharField(max_length=512)
    is_active = models.BooleanField(default=True)
    user_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="listings")
    category_id = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.title}: ${self.starting_price}"