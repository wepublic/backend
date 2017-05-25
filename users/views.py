from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from users.permissions import UserViewPermission
from users.models import Userprofile
from users.serializers import RegisterSerializer, UserSerializer, TokenSerializer
from users import utils
from rest_framework import exceptions
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.

    retrieve:
    Return a user instance.

    list:
    Return all users, ordered by most recently joined.

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserViewPermission]

    @list_route(methods=['post'])
    def token(self, request):
        """
        Acquire an API token by posting your credentials
        """
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        if user is not None:
            token, su = Token.objects.get_or_create(user=user)
            response = {'Token': token.key }
            return Response(response)
        else:
            raise exceptions.AuthenticationFailed
        
    @list_route(methods=['get'],authentication_classes=[TokenAuthentication], permission_classes=[IsAuthenticated])
    def logout(self, request):
        user = self.get_object()
        Token.objects.get(user=user).delete()
        response = {'status':'logged out'}
        return Response(response)

    @list_route(authentication_classes=[TokenAuthentication])
    def me(self, request):
        if request.user.pk is None:
            raise exceptions.NotAuthenticated
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def list(self, request):
        if utils.is_staff_user(request.user):
            serializer = self.get_serializer(self.get_queryset(), many=True)
        else:
            raise exceptions.PermissionDenied
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        userprofile = Userprofile(user=user)
        userprofile.save()
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(instance=user,data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({'status': 'ok'})
        


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
    permission_classes = (UserViewPermission,)
    queryset = User.objects.all()
    serializer_class=UserSerializer

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def get(self, request, pk, format=None):
        user = self.get_objects(pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = self.get_serializer(user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    



