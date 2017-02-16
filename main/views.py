from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "main/about.html"


class ContactFormSuccessView(TemplateView):
    template_name = "main/contact-form-success.html"


class ContactView(FormView):
    template_name = "main/contact.html"


class HomeView(TemplateView):
    template_name = "main/home.html"
