from django.urls import path
from .views import RegisterView
from .views import TestAuthWithView
from .views import GoogleLoginJWTView
from .views import OrganizationListCreateView
from .views import EventCreateView
from .views import EventListView
from .views import EventStatsView
from .views import EventCountView
from .views import EventDailyView
from .views import TopEventTypesView
from .views import DashboardView
from .views import LogoutView
from .views import FunnelAnalyticsView
from .views import MLTrainingDataView
from .views import MLPredictionView
from .views import PredictionValidationAPIView

urlpatterns = [
    path('signup/', RegisterView.as_view()),
    path('test/', TestAuthWithView.as_view()),
    path('oauth/jwt/', GoogleLoginJWTView.as_view()),
    path('organizations/', OrganizationListCreateView.as_view(), name='organizations'),
    path('event/', EventCreateView.as_view(), name='event-create'),
    path('event/list/', EventListView.as_view(), name='event-list'),
    path('event/stats/', EventStatsView.as_view(), name='event-stats'),
    path('event/count/', EventCountView.as_view(), name='event-count'),
    path('event/daily/', EventDailyView.as_view()),
    path('event/top/', TopEventTypesView.as_view()),
    path('dashboard/', DashboardView.as_view()),\
    path('logout/', LogoutView.as_view(), name='logout'),
    path('analytics/funnel/', FunnelAnalyticsView.as_view(), name='analytics'),
    path('ml/training-data', MLTrainingDataView.as_view(), name='ml-training-data'),
    path("ml/predict/", MLPredictionView.as_view()),
    path("ml/validate/", PredictionValidationAPIView.as_view(),
    path("health/", lambda request: JsonResponse({"status": "ok"}))
),
]