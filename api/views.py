from django.shortcuts import render
from django.http import HttpResponseForbidden
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
import django_filters
from . import serializers
from . import models
from django.contrib.auth.models import User


class Pagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class MeetingRoomView(viewsets.ModelViewSet):
    model = models.MeetingRoom
    queryset = models.MeetingRoom.objects.all()
    serializer_class = serializers.MeetingRoomSerializer
    pagination_class = Pagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    ordering_fields = ['amount_people']
    ordering = ['amount_people']
    search_fields = ['name', ]
    filterset_fields = ['name', 'amount_people']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)


class ReservationFilterSet(FilterSet):
    def start_date_time_filter(self, queryset, name, value):
        start_date_time = self.request.query_params.get('start_date_time', None)
        if start_date_time is not None:
            queryset = queryset.filter(start_date_time__gte=start_date_time)
            return queryset

    def end_date_time_filter(self, queryset, name, value):
        end_date_time = self.request.query_params.get('end_date_time', None)
        if end_date_time is not None:
            queryset = queryset.filter(end_date_time__lte=end_date_time)
            return queryset

    start_date_time = django_filters.Filter(field_name="start_date_time", label="StartDateTime",
                                            method='start_date_time_filter')
    end_date_time = django_filters.Filter(field_name="end_date_time", label="EndDateTime",
                                          method='end_date_time_filter')

    class Meta:
        model = models.Reservation
        fields = ['start_date_time', 'end_date_time']


class ReservationView(viewsets.ModelViewSet):
    model = models.Reservation
    queryset = models.Reservation.objects.all()
    serializer_class = serializers.ReservationSerializer
    pagination_class = Pagination
    filter_class = ReservationFilterSet
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    ordering_fields = ['start_date_time', 'end_date_time']
    ordering = ['start_date_time', 'end_date_time']
    search_fields = ['title', ]
    filterset_fields = ['employees', 'title', 'meeting_room', 'start_date_time', 'end_date_time']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        meetings = len(models.Reservation.objects.filter(meeting_room=request.data['meeting_room'],
                                                         start_date_time__gte=request.data['start_date_time'],
                                                         end_date_time__lte=request.data['end_date_time']).exclude(id=instance.id))
        meetings += len(models.Reservation.objects.filter(meeting_room=request.data['meeting_room'],
                                                          start_date_time__lte=request.data['start_date_time'],
                                                          end_date_time__gte=request.data['end_date_time']).exclude(id=instance.id))
        if self.request.user.id in list(instance.employees.all().values_list('id', flat=True)) and meetings == 0:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()

    def create(self, request, *args, **kwargs):
        meetings = len(models.Reservation.objects.filter(meeting_room=request.data['meeting_room'],
                                                         start_date_time__gte=request.data['start_date_time'],
                                                         end_date_time__lte=request.data['end_date_time']))
        meetings += len(models.Reservation.objects.filter(meeting_room=request.data['meeting_room'],
                                                          start_date_time__lte=request.data['start_date_time'],
                                                          end_date_time__gte=request.data['end_date_time']))
        if meetings == 0:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response("Meeting room you are trying to book is already booked for that time",
                            status=status.HTTP_409_CONFLICT)


class UserRegisterView(viewsets.ModelViewSet):
    model = User
    queryset = User.objects
    serializer_class = serializers.UserSerializer
    http_method_names = ['post']
    permission_classes = [AllowAny]


class UserGetUpdateView(viewsets.ModelViewSet):
    model = User
    queryset = User.objects
    serializer_class = serializers.UserSerializer
    http_method_names = ['get', 'patch']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = User.objects.filter(id=self.request.user.id)
        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.id == self.request.user.id:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return HttpResponseForbidden()
