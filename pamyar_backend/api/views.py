# api/views.py

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, TodoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Todo, User, Profile
from .serializers import TodoSerializer, UserSerializer
from django.shortcuts import get_object_or_404 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ProfileSerializer, ChangePasswordSerializer
from .models import VoiceHistory
from .serializers import VoiceHistorySerializer
from rest_framework import generics
from .models import Objective, KeyResult
from .serializers import ObjectiveSerializer, KeyResultSerializer
from .models import Todo, User, Profile, VoiceHistory, Objective 
from .rag_system import AnswerGenerator
from .rag_system import rag_generator_instance
import google.generativeai as genai
from . import config 
from .models import ChatHistory
from .serializers import (
    TodoSerializer, 
    UserSerializer, 
    ProfileSerializer, 
    ChangePasswordSerializer, 
    VoiceHistorySerializer, 
    KeyResultSerializer, 
    ObjectiveSerializer,
    ChatHistorySerializer
)



class VoiceHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        voice_notes = VoiceHistory.objects.filter(user=request.user).order_by('-created_at')
        serializer = VoiceHistorySerializer(voice_notes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if 'audio_file' not in request.FILES:
            return Response({'error': 'فایل صوتی ارسال نشده.'}, status=status.HTTP_400_BAD_REQUEST)
        
   
        voice_note = VoiceHistory.objects.create(
            user=request.user,
            audio_file=request.FILES['audio_file']
        )
        
        serializer = VoiceHistorySerializer(voice_note, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VoiceHistoryDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            voice_note = VoiceHistory.objects.get(pk=pk, user=request.user)
            voice_note.delete() 
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VoiceHistory.DoesNotExist:
            return Response({'error': 'پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND)


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response({'message': 'ثبت نام موفق بود', 'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '').lower()
        password = request.data.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:

            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'ایمیل یا رمز عبور اشتباه است'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'خروج با موفقیت انجام شد'}, status=status.HTTP_200_OK)



class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)

        avatar_url = None
        if profile.avatar and hasattr(profile.avatar, 'url'):
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        data = {
            'email': user.email,
            'username': user.username, 
            'avatar_url': avatar_url
        }
        return Response(data, status=status.HTTP_200_OK)


class ChangeAvatarView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
    
        serializer = ProfileSerializer(profile, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            
         
            response_data = {
                'message': 'عکس پروفایل با موفقیت آپدیت شد.',
                'avatar_url': serializer.data.get('avatar_url')
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')
            
            if not user.check_password(old_password):
                return Response({'error': 'رمز عبور فعلی اشتباه است.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            return Response({'message': 'رمز عبور با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({'message': 'خروج با موفقیت انجام شد.'}, status=status.HTTP_200_OK) 


# ---برای تودولیست---
class TodoListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #  برای گرفتن لیست کارها
    def get(self, request):
        todos = Todo.objects.filter(user=request.user).order_by('-created_at')
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #  برای افزودن کار جدید
    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Todo, pk=pk, user=user)


    def patch(self, request, pk):
        todo = self.get_object(pk, request.user)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        todo = self.get_object(pk, request.user)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class KeyResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KeyResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return KeyResult.objects.filter(objective__user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object() 
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save() 
        return Response(serializer.data)

    

class ObjectiveListView(generics.ListCreateAPIView):
    serializer_class = ObjectiveSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
  
        return Objective.objects.filter(user=self.request.user, is_archived=False)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ObjectiveDetailView(generics.RetrieveUpdateDestroyAPIView):
     serializer_class = ObjectiveSerializer
     permission_classes = [IsAuthenticated]
     def get_queryset(self):
         return Objective.objects.filter(user=self.request.user)
         

class KeyResultCreateView(generics.CreateAPIView):
    serializer_class = KeyResultSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        objective = get_object_or_404(Objective, pk=self.kwargs['objective_pk'], user=self.request.user)
    
        key_result = serializer.save(objective=objective)
        key_result.current_value = key_result.start_value
        key_result.save()

from .models import KPI
from .serializers import KPISerializer


class KPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KPISerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return KPI.objects.filter(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
 
        
        print("\n--- Inside KPIDetailView (partial_update) ---")
        
        kpi_id = self.kwargs.get('pk')
        print(f"Request received to update KPI with ID: {kpi_id}")
        

        print("Data received from frontend:", request.data)
        
        try:
            response = super().partial_update(request, *args, **kwargs)
            

            print(f"SUCCESS: KPI {kpi_id} updated. Response status: {response.status_code}")
            print("------------------------------------------\n")
            
            return response

        except Exception as e:
            print(f"ERROR: An exception occurred while updating KPI {kpi_id}: {e}")
            print("------------------------------------------\n")
            raise e 
        

     
from .rag_system import AnswerGenerator

try:
    print("--- Configuring genai with API key from config ---")
    genai.configure(api_key=config.GEMINI_API_KEY)
    rag_generator = AnswerGenerator.get_instance()
    print("✅ RAG system instance created successfully.")
except Exception as e:
    print(f"❌ FAILED TO INITIALIZE RAG SYSTEM: {e}")
    rag_generator = None



class ChatView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
       
    def post(self, request, *args, **kwargs):
        """
     
        """
        user_input = request.data.get('message', '')
        if not user_input:
            return Response({'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
        

        if not rag_generator or not rag_generator.model:
             return Response(
                 {'reply': 'سیستم هوش مصنوعی چت در حال حاضر در دسترس نیست.'}, 
                 status=status.HTTP_503_SERVICE_UNAVAILABLE
             )

      
        response_text = rag_generator.generate_answer(user_input, request.user) 
        
        return Response({'reply': response_text}, status=status.HTTP_200_OK)
    


class ChatHistoryView(generics.ListAPIView):
    """

    """
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
  
        return ChatHistory.objects.filter(user=self.request.user, session_type='text').order_by('created_at')