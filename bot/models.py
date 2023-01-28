from django.core.validators import MinLengthValidator
from django.db import models


from django.utils.crypto import get_random_string


class TgUser(models.Model):
    class Meta:
        verbose_name = "Пользователь телеграм"
        verbose_name_plural = "Пользователи телеграм"

    tg_user_id = models.BigIntegerField(verbose_name="ID пользователя в телеграм")
    tg_chat_id = models.BigIntegerField(verbose_name="ID чата в телеграм", unique=True)
    tg_username = models.CharField(max_length=32, validators=[MinLengthValidator(5)])
    verification_code = models.CharField(max_length=10, verbose_name="Код для верификации")
    user = models.ForeignKey(
        'core.User', verbose_name="Связанный пользователь приложения", on_delete=models.CASCADE, null=True
    )

    def set_verification_code(self) -> str:
        """Генерация случайного кода верификации"""
        code = get_random_string(10)
        self.verification_code = code
        self.save()
        return code

