from django.contrib import admin

from django.contrib import admin
from .models import Profile, Todo, ChatHistory, VoiceHistory, Objective, KeyResult, KPI
admin.site.register(Profile)
admin.site.register(Todo)
admin.site.register(ChatHistory)
admin.site.register(VoiceHistory)
admin.site.register(Objective)
admin.site.register(KeyResult)
admin.site.register(KPI)