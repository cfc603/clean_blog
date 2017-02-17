from django.conf.urls import url

from main import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home"),
    url(r'^about/$', views.AboutView.as_view(), name="about"),
    url(r'^contact/$', views.ContactView.as_view(), name="contact"),
    url(r'^contact-form-success/$', views.ContactFormSuccessView.as_view(), name="contact_form_success"),
    url(r'^post/(?P<pk>[\d]+)/(?P<slug>[-\w]+)/$', views.BlogDetailView.as_view(), name="post"),
]
