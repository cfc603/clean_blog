from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from main.forms import ContactForm


class AboutViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:about"))
        self.assertTemplateUsed(response, "main/about.html")


class BlogDetailView(TestCase):
    def test_renders_correct_template(self):
        post = mommy.make("main.Blog")
        response = self.client.get(
            reverse("main:post", args=[str(post.id), post.slug])
        )
        self.assertTemplateUsed(response, "main/post.html")


class ContactFormSuccessViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:contact_form_success"))
        self.assertTemplateUsed(response, "main/contact-form-success.html")


class ContactViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:contact"))
        self.assertTemplateUsed(response, "main/contact.html")

    def test_uses_contact_form_as_form_class(self):
        response = self.client.get(reverse("main:contact"))
        self.assertIsInstance(response.context['form'], ContactForm)

    def test_uses_correct_success_url(self):
        response = self.client.post(reverse("main:contact"), {
                "name": "test name",
                "email": "test@test.com",
                "message": "test message",
            })
        self.assertRedirects(response, reverse("main:contact_form_success"))


class HomeViewTest(TestCase):

    def test_renders_correct_template(self):
        response = self.client.get(reverse("main:home"))
        self.assertTemplateUsed(response, "main/home.html")

    def test_get_queryset(self):
        # only live blog posts
        posts = mommy.make("main.Blog", _quantity=10)
        live_posts = mommy.make("main.Blog", live=True, _quantity=5)
        response = self.client.get(reverse("main:home"))
        self.assertEqual(5, response.context['object_list'].count())
