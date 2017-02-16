from django.core.urlresolvers import reverse
from django.test import TestCase


class HomeViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:home"))
        self.assertTemplateUsed(response, "main/home.html")
