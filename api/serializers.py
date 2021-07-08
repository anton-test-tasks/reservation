from rest_framework import serializers
from . import models
from django.contrib.auth.models import User


class MeetingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MeetingRoom
        fields = ('id', 'url', 'name', 'amount_people')
        read_only_fields = ('id', 'url',)

    def create(self, validated_data):
        meeting_room = models.MeetingRoom(**validated_data)
        meeting_room.save()
        return meeting_room

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.amount_people = validated_data.get('amount_people', instance.amount_people)
        instance.save()
        return instance


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reservation
        fields = ('id', 'url', 'title', 'meeting_room', 'start_date_time', 'end_date_time', 'employees')
        read_only_fields = ('id', 'url')

    def create(self, validated_data):
        employees = validated_data.pop('employees')
        reservation = models.Reservation.objects.create(**validated_data)
        reservation.employees.set(employees)
        reservation.save()
        return reservation

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.start_date = validated_data.get('start_date_time', instance.start_date_time)
        instance.end_date = validated_data.get('end_date_time', instance.end_date_time)
        instance.meeting_room = validated_data.get('meeting_room', instance.meeting_room)
        instance.employees.set(validated_data.get('employees', instance.employees.all()))
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'first_name', 'last_name', 'password')
        read_only_fields = ('id', 'url',)
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
