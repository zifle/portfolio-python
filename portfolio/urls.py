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
    path('api/categories', views.CategoryIndex.as_view(), name='categories'),
    path('api/categories/<int:id>', views.CategoryDetail.as_view(), name='category'),
    path('api/albums', views.AlbumIndex.as_view(), name='albums'),
    path('api/albums/<int:id>', views.AlbumDetail.as_view(), name='album'),
    path('api/albums/<slug:id>', views.AlbumDetail.as_view(), name='album'),
    path('api/albums/<int:id>/toggle-publish', views.albumTogglePublish, name='album_publish_toggle'),
    path('api/albums/<int:id>/upload', views.AlbumUpload.as_view(), name='album_upload'),
    path('api/locations', views.LocationsIndex.as_view(), name='locations'),
    path('api/cameras', views.camerasIndex, name='cameras'),
    path('api/lenses', views.lensIndex, name='lenses'),

    # Catch all non-captured requests, so we can show our SPA
    path('', views.index_view, {"resource": ""}, name='index'),
    path('<path:resource>', views.index_view, name='login'),
]
