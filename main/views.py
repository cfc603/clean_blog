from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "main/about.html"


class HomeView(TemplateView):
    template_name = "main/home.html"
