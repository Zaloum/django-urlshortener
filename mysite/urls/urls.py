from django.conf.urls import url

from . import views

app_name = 'urls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name = 'index'), 
    url(r'^create/$', views.CreateURLView.as_view(), name = 'create'), 
    url(r'^(?P<short>[A-Za-z0-9]+)/', views.RedirectURLView.as_view(), name = 'redirect'), 
]
