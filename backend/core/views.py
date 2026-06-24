from django.shortcuts import render
from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import get_user_organization
from .serializers import OrganizationSerializer, EventSerializer
from .models import Organization, Event, Membership
from django.db.models import Count 
from django.utils.dateparse import parse_date
import django_rq
from core.tasks.event_tasks import create_event_async
from django.db.models.functions import TruncDate
from .utils import get_org_and_validate
from .services.dashboard import get_total_events, get_events_per_day, get_top_event_types, get_recent_events
from django.core.cache import cache
from rest_framework.permissions import AllowAny


from sklearn.linear_model import LinearRegression


import os
API_KEY = os.getenv("API_KEY")

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class TestAuthWithView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = get_user_organization(request.user)


        return Response({
            "message": "You are authenticated!",
            "organization": org.name if org else "No organization"
            })


class GoogleLoginJWTView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email
        })

class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .models import Membership
        org_ids = Membership.objects.filter(user=self.request.user).values_list('organization_id', flat=True)
        return Organization.objects.filter(id__in=org_ids)

    def perform_create(self, serializer):
        print("Current user:", self.request.user.id, self.request.user.username)
        org = serializer.save(owner=self.request.user)
        Event.objects.create(
            organization=org,
            user=self.request.user,
            event_type='organization_created',
            event_data={'organization_id': org.id, 'organization_name': org.name}
        )

        from .models import Membership
        Membership.objects.create(
            user=self.request.user,
            organization=org,
            role='admin'
        )


class EventCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        org_id = request.data.get("organization")

        try:
            membership = Membership.objects.get(
                user=request.user,
                organization_id=org_id
            )
        except Membership.DoesNotExist:
            return Response(
                {"error": "Not part of organization"},
                status=403
            )

        org = membership.organization
        
        serializer = EventSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():

            event_queue = django_rq.get_queue('events')
            cache_queue = django_rq.get_queue('cache')
            analytics_queue = django_rq.get_queue('analytics')
            notification_queue = django_rq.get_queue('notifications')
            job = event_queue.enqueue(
                create_event_async, 
                org_id=org.id,
                event_type=request.data.get('event_type'),
                event_data=request.data.get('event_data', {}),
                user_id=request.user.id
                )
            
            return Response({"message": "Event queued"}, status=202)

        return Response(serializer.errors, status=400)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Event, Organization, Membership
from .serializers import EventSerializer


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = self.request
        api_key = request.headers.get("X-MY-SECRET-KEY")

        if not api_key:
            raise PermissionDenied("API key is required")

        # ✅ Get organization from API key
        try:
            org = Organization.objects.get(api_key=api_key)
        except Organization.DoesNotExist:
            raise PermissionDenied("Invalid API key")

        # ✅ Membership check
        is_member = Membership.objects.filter(
            user=request.user,
            organization=org
        ).exists()

        if not is_member:
            raise PermissionDenied("You are not part of this organization")

        # ✅ ONLY this org's events
        queryset = Event.objects.filter(organization=org)

        # ✅ FILTER (event_type)
        event_type = request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset.order_by('-created_at')

class EventStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.all()

        organization_id = request.query_params.get('organization')
        if organization_id:
            events = events.filter(organization_id=organization_id)

        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        if start_date:
            start_date = parse_date(start_date)
            events = events.filter(created_at__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            events = events.filter(created_at__lte=end_date)

        total_events = events.count()

        event_type_counts = (
            events.values('event_type')
            .annotate(count=Count('event_type'))
        )

        event_type_dict = {
            item['event_type']: item['count']
            for item in event_type_counts
        }

        return Response({
            "total_events": total_events,
            "event_types": event_type_dict
        })

class EventCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        key = request.headers.get("X-MY-SECRET-KEY")

        try:
            org = Organization.objects.get(api_key=key)
        except Organization.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=403)

        is_member = Membership.objects.filter(
            user=request.user,
            organization=org
        ).exists()

        if not is_member:
            return Response({"error": "You are not part of this organization"}, status=403)
            

        total_events = Event.objects.filter(organization=org).count()

        return Response({
            "total_events": total_events
        })

class EventDailyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        key = request.headers.get("X-MY-SECRET-KEY")

        try:
            org = Organization.objects.get(api_key=key)
        except Organization.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=403)

        is_member = Membership.objects.filter(
            user=request.user,
            organization=org
        ).exists()

        if not is_member:
            return Response({"error": "You are not part of this organization"}, status=403)

        events = {
            Event.objects
            .filter(organization=org)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        }

        return Response(events)
    
class TopEventTypesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        api_key = request.headers.get("X-MY-SECRET-KEY")


        # ✅ API key → organization
        try:
            org = Organization.objects.get(api_key=api_key)
        except Organization.DoesNotExist:
            return Response({"error": "Invalid API key"}, status=403)

        # ✅ Membership check
        is_member = Membership.objects.filter(
            user=request.user,
            organization=org
        ).exists()

        if not is_member:
            return Response({"error": "You are not part of this organization"}, status=403)

        # ✅ AGGREGATION
        events = (
            Event.objects
            .filter(organization=org)
            .values('event_type')
            .annotate(count=Count('id'))
            .order_by('-count')  # highest first
        )

        return Response(events)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_id = request.query_params.get('organization')

        # 🔒 STEP 1: Get ONLY orgs user belongs to
        user_orgs = Organization.objects.filter(
            membership__user=request.user
        )

        # 🔒 STEP 2: Validate org access
        if org_id:
            org = user_orgs.filter(id=org_id).first()
        else:
            org = user_orgs.first()

        if not org:
            return Response(
                {"error": "No access to this organization"},
                status=403
            )

        # 🔒 STEP 3: Parse filters
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')

        start_date = parse_date(start_date) if start_date else None
        end_date = parse_date(end_date) if end_date else None

        # 🔒 STEP 4: Cache key (org-scoped = safe)
        cached_key = f"dashboard:{org.id}:{start_date}:{end_date}"

        cached_data = cache.get(cached_key)
        if cached_data:
            return Response(cached_data)

        # 🔒 STEP 5: Build response (STRICTLY org-scoped)
        data = {
            "total_events": get_total_events(org, start_date, end_date),
            "events_per_day": get_events_per_day(org, start_date, end_date),
            "top_event_types": get_top_event_types(org, start_date, end_date),
            "recent_events": get_recent_events(org, start_date, end_date),
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }

        # 🔒 STEP 6: Save cache
        cache.set(cached_key, data, timeout=10)

        return Response(data)


class LogoutView(APIView):

    def post(self, request):
        res = Response({"message": "Logged out"}, status=200)

        res.delete_cookie("access_token", path="/")
        res.delete_cookie("refresh_token", path="/")

        return res

        
class FunnelAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # =========================
        # STEP 1: GET USER ORGS (SECURE)
        # =========================
        org_id = request.query_params.get("organization")

        user_orgs = Organization.objects.filter(
            membership__user=request.user
        )

        if org_id:
            org = user_orgs.filter(id=org_id).first()
        else:
            org = user_orgs.first()

        if not org:
            return Response(
                {"error": "No access to this organization"},
                status=403
            )

        # =========================
        # STEP 2: DEFINE FUNNEL
        # =========================
        FUNNEL_STEPS = [
            "test_Live_Dashboard",
            "test_check_Websocket",
            "test_looping",
            "test_check_API",
            "test_check_CACHING",
            "test_movie",
            "test_Shit"
        ]

        # =========================
        # STEP 3: BUILD FUNNEL DATA
        # =========================
        funnel_data = []

        for step in FUNNEL_STEPS:

            users_count = (
                Event.objects
                .filter(
                    organization=org,
                    event_type=step
                )
                .values("user")   # important: unique users
                .distinct()
                .count()
            )

            funnel_data.append({
                "event": step,
                "users": users_count
            })

        # =========================
        # STEP 4: CONVERSION RATE
        # =========================
        for i in range(1, len(funnel_data)):

            prev_users = funnel_data[i - 1]["users"]
            current_users = funnel_data[i]["users"]

            conversion_rate = 0

            if prev_users > 0:
                conversion_rate = (current_users / prev_users) * 100

            funnel_data[i]["conversion_rate"] = round(conversion_rate, 2)

        # =========================
        # STEP 5: RESPONSE
        # =========================
        return Response({
            "organization": org.name,
            "funnel": funnel_data
        })

class MLTrainingDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        org_id = request.query_params.get("organization")

        user_orgs = Organization.objects.filter(
            membership__user=request.user
           
        )

        if org_id:
            org = user_orgs.filter(id=org_id).first()
        else:
            org = user_orgs.first()

        if not org:
            return Response(
                {"error": "No access to this organization"},
                status=403
            )

        daily_events =  (
            Event.objects
            .filter(organization=org)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        dataset = []

        for item in daily_events:
            dataset.append({
                "date": item['date'],
                "event_count": item['count']
            })

        return Response({
            "organization": org.name,
            "dataset": dataset
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Count
from django.db.models.functions import TruncDate

from sklearn.linear_model import LinearRegression

from core.models import Event, Organization


class MLPredictionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        membership = Membership.objects.filter(
            user=request.user
        ).select_related('organization').first()

        if not membership:
            return Response(
                {"error": "No access to any organization"},
                status=403
            )

        org = membership.organization
        role = membership.role
 
        if not role:
            return Response(
                {"error": "No access to this organization or it does not exist"},
                status=403
            )


        # =========================
        # STEP 2: GET DAILY EVENTS
        # =========================
        daily_events = (
            Event.objects
            .filter(organization=org)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(total_events=Count("id"))
            .order_by("date")
        )

        # =========================
        # STEP 3: PREPARE X AND y
        # =========================
        X = []
        y = []

        for index, item in enumerate(daily_events):

            # X = day number
            X.append([index + 1])

            # y = total events
            y.append(item["total_events"])

        # =========================
        # STEP 4: VALIDATE DATA
        # =========================
        if len(X) < 2:
            return Response({
                "error": "Not enough data for prediction"
            })

        # =========================
        # STEP 5: CREATE MODEL
        # =========================
        model = LinearRegression()

        # =========================
        # STEP 6: TRAIN MODEL
        # =========================
        model.fit(X, y)

        # =========================
        # STEP 7: PREDICT NEXT DAY
        # =========================
        next_day = [[len(X) + 1]]

        prediction = model.predict(next_day)

        # =========================
        # STEP 8: TREND DETECTION
        # =========================
        trend = "stable"

        if len(y) >= 2:

            if y[-1] > y[-2]:
                trend = "increasing"

            elif y[-1] < y[-2]:
                trend = "decreasing"

        # =========================
        # STEP 9: RESPONSE
        # =========================
        return Response({

            "organization": org.name,

            "historical_data": y,

            "prediction_next_day": round(
                prediction[0],
                2
            ),

            "trend": trend,

            "training_points": len(X),
            "role": role,
            "org": org.id
        })

class PredictionValidationAPIView(APIView):
    from core.services.ml_service import PredictionService
    from core.services.validation_service import PredictionValidationService

    permission_classes = [IsAuthenticated]

    def get(self, request):

            org_id = request.query_params.get(
                "organization"
            )

            user_orgs = Organization.objects.filter(
                membership__user=request.user
            )

            if org_id:
                org = user_orgs.filter(
                    id=org_id
                ).first()
            else:
                org = user_orgs.first()

            if not org:
                return Response(
                    {"error": "No access"},
                    status=403
                )

            # =========================
            # HISTORICAL DATA
            # =========================

            daily_events = (
                Event.objects
                .filter(
                    organization=org
                )
                .annotate(
                    date=TruncDate("created_at")
                )
                .values("date")
                .annotate(
                    total_events=Count("id")
                )
                .order_by("date")
            )

            values = [
                item["total_events"]
                for item in daily_events
            ]

            if len(values) < 3:
                return Response({
                    "error": "Not enough data"
                })

            # =========================
            # PREDICT LAST DAY
            # =========================

            historical_values = values[:-1]

            actual = values[-1]

            prediction_service = self.PredictionService()

            predicted = (
                prediction_service.train_and_predict(historical_values)
            )

            validation_service = (
                self.PredictionValidationService()
            )

            result = (
                validation_service.calculate_error(
                    actual=actual,
                    predicted=predicted)
            )

            return Response({
                "organization": org.name,
                **result
            })








            