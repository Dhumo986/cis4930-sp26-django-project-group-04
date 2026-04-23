from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('records/', views.track_list, name='track_list'),
    path('records/add/', views.track_create, name='track_create'),
    path('records/<int:pk>/', views.track_detail, name='track_detail'),
    path('records/<int:pk>/edit/', views.track_update, name='track_update'),
    path('records/<int:pk>/delete/', views.track_delete, name='track_delete'),
    path('search/', views.track_list_view, name='track_search'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('fetch/', views.fetch_data_view, name='fetch_data'),
]
