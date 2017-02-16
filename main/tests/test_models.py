from django.test import TestCase

from model_mommy import mommy


class BlogTest(TestCase):

    def test_unicode(self):
        blog = mommy.make("main.Blog")
        self.assertEqual(blog.__unicode__(), blog.title)

    def test_slug(self):
        blog = mommy.make("main.Blog", title="Here Is A Test title")
        self.assertEqual(blog.slug, "here-is-a-test-title")


class CategoryTest(TestCase):

    def test_unicode(self):
        category = mommy.make("main.Category")
        self.assertEqual(category.__unicode__(), category.title)

    def test_slug(self):
        category  = mommy.make(
            "main.Category", title="Test Category Title"
        )
        self.assertEqual(category.slug, "test-category-title")
