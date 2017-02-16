from django.core.urlresolvers import reverse
from django.test import TestCase


class AboutViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:about"))
        self.assertTemplateUsed(response, "main/about.html")


class ContactViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:contact"))
        self.assertTemplateUsed(response, "main/contact.html")


class HomeViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:home"))
        self.assertTemplateUsed(response, "main/home.html")
