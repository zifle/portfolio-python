from django.urls import path
from . import views

app_name = 'portfolio'
urlpatterns = [
    # Auth paths
    path('auth/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('auth/login', views.login_view, name='login'),
    path('auth/logout', views.logout_view, name='logout'),
    path('auth/user', views.user, name='user'),

    # API Paths
    path('api/albums', views.AlbumIndex, name='albums'),
    path('api/<slug:slug>/', views.AlbumView.as_view(), name='album'),

    # Catch all non-captured requests, so we can show our SPA
    path('', views.index_view, {"resource": ""}, name='index'),
    path('<path:resource>', views.index_view, name='login'),
]