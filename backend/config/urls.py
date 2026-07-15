from django.contrib import admin
from django.urls import path
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from customResponse.cookieResponse import CookieTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/login/', CookieTokenObtainPairView.as_view()),
    path('api/login/refresh/', TokenRefreshView.as_view()),
    path('django-rq/', include('django_rq.urls')),

    path('accounts/', include('allauth.urls')),  # Include allauth URLs
]
