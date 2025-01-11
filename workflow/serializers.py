from rest_framework import serializers
from .models import Agent, Case, Callback, CaseNote
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Agent
        fields = ('id', 'user', 'employee_id', 'is_active')

class CaseNoteSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.user.username', read_only=True)
    
    class Meta:
        model = CaseNote
        fields = ('id', 'agent_name', 'content', 'sentiment_score', 'created_at')

class CallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Callback
        fields = ('id', 'scheduled_time', 'completed', 'notes', 'created_at')

class CaseSerializer(serializers.ModelSerializer):
    assigned_agent = AgentSerializer(read_only=True)
    notes = CaseNoteSerializer(many=True, read_only=True)
    callbacks = CallbackSerializer(many=True, read_only=True)
    
    class Meta:
        model = Case
        fields = ('id', 'case_id', 'client_name', 'description', 'status', 
                 'priority', 'assigned_agent', 'created_at', 'updated_at', 
                 'date_closed', 'notes', 'callbacks')
