from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAllowedToViewAndChangeUsers
# Create your views here.

class RegisterAPIView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        #create the Serializer and validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # create and return token
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class LogOutAPIView(APIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class UserViewAPI(APIView):
    permission_classes = (IsAuthenticated, IsAllowedToViewAndChangeUsers)
    queryset = User.objects.all()
    



