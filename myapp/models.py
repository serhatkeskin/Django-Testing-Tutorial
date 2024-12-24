from django.db import models

# Create your models here.
class MyModel(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class MyProduct(models.Model):
    name = models.CharField(max_length=100)
    unique_code = models.CharField(max_length=50, unique=True)  # unique_code must be unique
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.name
