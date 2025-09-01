# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Todo
from .models import Profile 
from .models import VoiceHistory
from .models import ChatHistory

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id', 'session_type', 'user_prompt', 'model_response', 'created_at']

class VoiceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceHistory
        fields = ['id', 'audio_file', 'transcription', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['avatar', 'avatar_url']
        read_only_fields = ['avatar_url']
        extra_kwargs = {
            'avatar': {'write_only': True} 
        }

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
    
        user = User.objects.create_user(
            username=validated_data['email'].lower(), 
            email=validated_data['email'].lower(),
            password=validated_data['password']
        )
        return user


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'text', 'completed', 'tag', 'created_at']
        read_only_fields = ['id', 'created_at']



from .models import Objective, KeyResult, KPI


class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = ['id', 'title', 'value', 'is_tracked']


class KeyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyResult
        fields = [
            'id', 
            'title', 
            'start_value', 
            'target_value', 
            'current_value', 
            'is_completed', 
            'progress'
        ]
       
        read_only_fields = [
            'id',
            'progress',
        ]

class ObjectiveSerializer(serializers.ModelSerializer):
    key_results = KeyResultSerializer(many=True, read_only=True)
    kpis = KPISerializer(many=True, read_only=True)
    class Meta:
        model = Objective
        fields = ['id', 'title', 'description', 'quarter', 'is_archived', 'key_results' , 'kpis']
        read_only_fields = ['id', 'key_results']

