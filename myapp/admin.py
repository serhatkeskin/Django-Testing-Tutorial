from django.contrib import admin
from .models import MyModel, MyProduct

# Register your models here.

admin.site.register(MyModel)
admin.site.register(MyProduct)