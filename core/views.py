from django.contrib.auth import (
    get_user_model,
    login,
    logout
)
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import (
    permissions,
    status
)
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView
)
from rest_framework.response import Response

from core.serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    UpdatePasswordSerializer
)


USER_MODEL = get_user_model()

# @extend_schema_view(
#     create=extend_schema(
#         description="Create new user", summary='New user'),
#     update=extend_schema(
#         description="Update user", summary='Update'),
# )
class RegistrationView(CreateAPIView):
    model = USER_MODEL
    serializer_class = RegistrationSerializer


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    @extend_schema(
        description="User login",
        summary="User login"
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)
        return Response(serializer.data)


class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = USER_MODEL.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Retrieve user info",
        summary="User info"
    )
    def get_object(self):
        return self.request.user

    @extend_schema(
        description="Destroy user",
        summary="Destroy user"
    )
    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    @extend_schema(
        description="Update user",
        summary="Update"
    )
    def get_object(self):
        return self.request.user



