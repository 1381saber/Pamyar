from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.db.models.signals import post_save
from django.dispatch import receiver

# api/models.py
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_avatars/', default='profile_avatars/my-default-avatar.png')

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



TAG_CHOICES = [
    ('product', 'فیچر و محصول'),
    ('planning', 'برنامه‌ریزی و هماهنگی'),
]

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    
    text = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='product')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

# api/models.py

class ChatHistory(models.Model):
 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_history')

    session_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('voice', 'Voice')], default='text')

    user_prompt = models.TextField()

    model_response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat with {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class VoiceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='voice_notes')
    transcription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class KPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    value = models.CharField(max_length=50)
    is_tracked = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Objective(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='objectives')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True) 
    quarter = models.CharField(max_length=50)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class KeyResult(models.Model):
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE, related_name='key_results')
    title = models.CharField(max_length=255)
    start_value = models.FloatField(default=0)
    target_value = models.FloatField()
    current_value = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    @property
    def progress(self):
        if self.target_value == self.start_value:
            return 100 if self.is_completed else 0
        progress = ((self.current_value - self.start_value) / (self.target_value - self.start_value)) * 100
        return min(max(progress, 0), 100)

    def __str__(self):
        return self.title