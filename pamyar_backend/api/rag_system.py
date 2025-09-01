# api/rag_system.py

import logging
import google.generativeai as genai
from . import config
from .prompts import QA_PROMPTS
from .models import ChatHistory
from django.contrib.auth.models import User
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger("rag_api")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AnswerGenerator:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'): return
        self._initialized = True
        
        self.model = None
        
        try:
            print("--- Initializing Gemini RAG model ---")
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name=config.GEMINI_MODEL_NAME,
                generation_config=config.GENERATION_CONFIG,
                system_instruction=QA_PROMPTS,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            print(f"✅ Gemini RAG model '{config.GEMINI_MODEL_NAME}' initialized successfully.")
        except Exception as e:
            print(f"❌ FAILED to initialize Gemini model. Error: {e}")
            self.model = None

    def generate_answer(self, user_input: str, user: User) -> str:
        if not self.model:
            return "Generation model is not available."

        try:

            past_conversations = ChatHistory.objects.filter(user=user, session_type='text').order_by('-created_at')[:20]
            

            history_for_api = []
            for entry in reversed(past_conversations):
                history_for_api.append({'role': 'user', 'parts': [{'text': entry.user_prompt}]})
                history_for_api.append({'role': 'model', 'parts': [{'text': entry.model_response}]})
            

            chat_session = self.model.start_chat(history=history_for_api)
            

            response = chat_session.send_message(user_input)
            

            ChatHistory.objects.create(
                user=user,
                session_type='text',
                user_prompt=user_input,
                model_response=response.text
            )
            
            return response.text

        except Exception as e:
            logger.error(f"Error in generate_answer for user {user.id}: {e}", exc_info=True)
            return "متاسفانه خطایی در تولید پاسخ رخ داد. لطفاً دوباره تلاش کنید."

rag_generator_instance = AnswerGenerator.get_instance()