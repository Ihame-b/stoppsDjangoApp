from django.urls import  path
from . import views
urlpatterns = [

    path('email/', views.index, name = 'index'),
]