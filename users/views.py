from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from users.permissions import UserViewPermission
from users.models import User
from users.serializers import UserSerializer
from users import utils
from rest_framework import exceptions
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validators
from django.utils import timezone
from rest_framework.renderers import TemplateHTMLRenderer
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
    def change_password(self, request):
        if 'email' not in request.data:
            raise exceptions.ParseError('\'email\' missing')
        if 'password' not in request.data:
            raise exceptions.ParseError('\'password\' missing')
        if 'new_password' not in request.data:
            raise exceptions.ParseError('\'new_password\' missing')

        user = authenticate(request,
                            email=request.data['email'],
                            password=request.data['password']
                            )
        if user is not None:
            try:
                validators.validate_password(
                        password=request.data['new_password'],
                        user=User
                        )
            except ValidationError as e:
                raise exceptions.ParseError(e)

            user.set_password(request.data['new_password'])
            user.save()
            user.remove_token()
            return Response({'Token': user.get_token().key})
        else:
            raise exceptions.AuthenticationFailed

    @list_route(methods=['post'])
    def token(self, request):
        """
        Acquire an API token by posting your credentials
        """
        if 'email' not in request.data or 'password' not in request.data:
            raise exceptions.ParseError(
                    detail="email and/or password field missing")
        user = authenticate(
                request,
                email=request.data['email'],
                password=request.data['password']
            )
        if user is not None:
            token, su = Token.objects.get_or_create(user=user)
            response = {'Token': token.key}
            return Response(response)
        else:
            raise exceptions.AuthenticationFailed

    @list_route(methods=['get'],
                authentication_classes=[TokenAuthentication],
                permission_classes=[IsAuthenticated])
    def logout(self, request):
        user = request.user
        Token.objects.get(user=user).delete()
        response = {'status': 'logged out'}
        return Response(response)

    @list_route(authentication_classes=[TokenAuthentication])
    def me(self, request):
        if request.user.pk is None:
            raise exceptions.NotAuthenticated
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def list(self, request):
        print('in list')
        if utils.is_staff_user(request.user):
            serializer = UserSerializer(User.objects.all(), many=True)
        else:
            raise exceptions.PermissionDenied
        return Response(serializer.data)

    def create(self, request):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        user.is_active = False
        user.save()
        user.send_validation_link(request)
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, partial=False, pk=None):
        print(partial)
        user = self.get_object()
        serializer = UserSerializer(user, request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({'status': 'ok'})

    @detail_route(methods=['GET'])
    def resend_validation(self, request, pk=None):
        user = self.get_object()
        user.send_validation_link(request)

        return Response("okay")

    @detail_route(methods=['GET'], renderer_classes=(TemplateHTMLRenderer, ))
    def activate(self, request, pk=None):
        activation_key = request.GET.get('key', '')

        if activation_key == '':
            raise exceptions.AuthenticationFailed('No activation key')
        user = self.get_object()
        if user.activation_key != activation_key:
            raise exceptions.AuthenticationFailed('key invalid')
        if timezone.now() > user.activation_key_exprires:
            raise exceptions.AuthenticationFailed('key expired')
        if user.is_active:
            return Response(template_name='users/activation_again.html')

        user.is_active = True
        user.save()

        return Response(template_name='users/activation_success.html')


class LogOutAPIView(APIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
