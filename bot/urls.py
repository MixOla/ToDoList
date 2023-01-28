from django.urls import path
import bot.views as views

urlpatterns = [
    path('verify', views.TgUserVerificationView.as_view()),
]

