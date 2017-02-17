from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import ContactForm
from .models import Blog


class AboutView(TemplateView):
    template_name = "main/about.html"


class BlogDetailView(DetailView):
    model = Blog
    template_name = "main/post.html"


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


class HomeView(ListView):
    model = Blog
    template_name = "main/home.html"
    paginate_by = 5

    def get_queryset(self):
        queryset = super(HomeView, self).get_queryset()
        return queryset.filter(live=True)
