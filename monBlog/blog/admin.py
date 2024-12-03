from django.contrib import admin
from .models import POST, Category, Tag

admin.site.register(POST)
admin.site.register(Category)
admin.site.register(Tag)