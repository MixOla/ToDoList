from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from .models import TgUser


class TgUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = "__all__"
        read_only_fields = ("tg_user_id", "tg_chat_id")

    def validate(self, attrs):
        verification_code = attrs.get("verification_code")
        tg_user = TgUser.objects.filter(verification_code=verification_code).first()
        if not tg_user:
            raise ValidationError({"verification_code": "field is incorrect"})
        attrs["tg_user"] = tg_user
        return attrs