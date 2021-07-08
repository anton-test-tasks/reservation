from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'reservation', views.ReservationView)
router.register(r'meeting_room', views.MeetingRoomView)
router.register(r'user/register', views.UserRegisterView)
router.register(r'user', views.UserGetUpdateView)


urlpatterns = [
    path('/', include(router.urls)),
]
