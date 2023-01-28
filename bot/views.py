from django.conf import settings
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .models import TgUser
from .serializers import TgUserUpdateSerializer
from .tg.client import TgClient


class TgUserVerificationView(GenericAPIView):
    model = TgUser
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserUpdateSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tg_user = serializer.validated_data["tg_user"]
        tg_user.user = self.request.user
        tg_user.save(update_fields=["user"])
        instance_serializer = self.get_serializer(tg_user)
        tg_client = TgClient(settings.BOT_TOKEN)
        tg_client.send_message(tg_user.tg_chat_id, "[Верификация пройдена]")

        return Response(instance_serializer.data)