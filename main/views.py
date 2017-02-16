from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import ContactForm


class AboutView(TemplateView):
    template_name = "main/about.html"


class ContactFormSuccessView(TemplateView):
    template_name = "main/contact-form-success.html"


class ContactView(FormView):
    template_name = "main/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("main:contact_form_success")

    def form_valid(self, form):
        form.send_email()
        form.send_confirmation()
        return super(ContactView, self).form_valid(form)


class HomeView(TemplateView):
    template_name = "main/home.html"
