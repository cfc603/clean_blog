from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify


class CreatedUpdated(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Blog(CreatedUpdated):
    title = models.CharField(max_length=100)
    body = models.TextField()
    image = models.ImageField(upload_to="blog_images/%Y/%m/%d/")
    live = models.BooleanField(default=False)
    category = models.ManyToManyField("main.Category")

    class Meta:
        ordering = ['-modified_date']

    def __unicode__(self):
        return '%s' % self.title

    @property
    def slug(self):
        return slugify(self.title)

    def get_absolute_url(self):
        return reverse("main:post", args=[str(self.id), self.slug])


class Category(CreatedUpdated):
    title = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.title

    @property
    def slug(self):
        return slugify(self.title)
