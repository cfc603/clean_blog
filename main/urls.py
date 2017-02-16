from django.conf.urls import url

from main import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="home"),
    # url(r'^another/$', views.another_view, name='another'),
]
