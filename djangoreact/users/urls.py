from django.urls import include, path
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://127.0.0.1:3000' #배포 시 서버주소 변경 필요
    client_class = OAuth2Client

# 로그아웃 (토큰 없앰) : domain/users/auth/logout
# 회원가입 : domain/users/auth/register

urlpatterns = [
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path("auth/", include('dj_rest_auth.urls')),  # 권한 요청하는 url은 domain/users/auth/
    path("auth/register", include('dj_rest_auth.registration.urls')) # 회원 가입 url domain/users/auth/register
]