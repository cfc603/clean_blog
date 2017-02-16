from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "main/about.html"


class ContactView(TemplateView):
    template_name = "main/contact.html"


class HomeView(TemplateView):
    template_name = "main/home.html"
