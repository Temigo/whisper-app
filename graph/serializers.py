from django.contrib.auth.models import User, Group
from .models import Graph, Infection
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class GraphSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(source='json_dumps')
    class Meta:
        model = Graph
        fields = ('name', 'data', 'description')

class InfectionSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(source='json_dumps')
    class Meta:
        model = Infection
        fields = ('graph', 'name', 'data')
