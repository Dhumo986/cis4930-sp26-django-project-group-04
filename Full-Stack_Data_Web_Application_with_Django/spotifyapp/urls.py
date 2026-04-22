from django.urls import path
from . import views

urlpatterns = [
    path('', views.track_list_view, name='track_list'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('fetch/', views.fetch_data_view, name='fetch_data'),
]
