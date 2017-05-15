from django.conf.urls import url
from users.views import RegisterAPIView, LogOutAPIView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
        url(r'^register/$', RegisterAPIView.as_view(), name='user_register'),
        url(r'^token/create/$', obtain_auth_token, name='user_get_token'),
        url(r'^token/delete/$', LogOutAPIView.as_view(), name='user_delete_token')
]
