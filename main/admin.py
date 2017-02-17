from django.contrib import admin

from .models import Blog, Category


admin.site.register(Category)


class CategoryInline(admin.TabularInline):
    model = Blog.category.through


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    inlines = (CategoryInline,)
    exclude = ('category',)
