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
    live = models.BooleanField(default=False)
    category = models.ManyToManyField("main.Category")

    def __unicode__(self):
        return '%s' % self.title

    @property
    def slug(self):
        return slugify(self.title)


class Category(CreatedUpdated):
    title = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.title

    @property
    def slug(self):
        return slugify(self.title)
