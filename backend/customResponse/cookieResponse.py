from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status


class CookieTokenObtainPairView(TokenObtainPairView):
     def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            res = Response({"message": "Login successful"}, status=status.HTTP_200_OK)

            res.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=60 * 60 * 24 * 7,  # 7 days
                path="/",
            )

            return res
            
        return response

