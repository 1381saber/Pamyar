from django.urls import path
from .views import (
    SignupView, 
    LoginView,
    LogoutView,
    TodoListView, 
    TodoDetailView,
    ChangeAvatarView,
    ChangePasswordView,
    UserProfileView,
    VoiceHistoryView,
    VoiceHistoryDetailView,
    ObjectiveListView,
    KeyResultDetailView,
    ObjectiveDetailView,
    KeyResultCreateView,
    KPIDetailView,
    ChatView,
    ChatHistoryView
)

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('todos/', TodoListView.as_view(), name='todo-list'),
    path('todos/<int:pk>/', TodoDetailView.as_view(), name='todo-detail'),
    path('profile/change-avatar/', ChangeAvatarView.as_view(), name='change-avatar'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('history/voice/', VoiceHistoryView.as_view(), name='voice-history'),
    path('history/voice/', VoiceHistoryView.as_view(), name='voice-history-list'),
    path('history/voice/<int:pk>/', VoiceHistoryDetailView.as_view(), name='voice-history-detail'),
    path('objectives/', ObjectiveListView.as_view(), name='objective-list'),
    path('objectives/<int:pk>/', ObjectiveDetailView.as_view(), name='objective-detail'),
    path('objectives/<int:objective_pk>/keyresults/', KeyResultCreateView.as_view(), name='keyresult-create'),
    path('keyresults/<int:pk>/', KeyResultDetailView.as_view(), name='keyresult-detail'),
    path('kpis/<int:pk>/', KPIDetailView.as_view(), name='kpi-detail'),
    path('chat/', ChatView.as_view(), name='text-chat'),
    path('history/chat/', ChatHistoryView.as_view(), name='chat-history'),
]



