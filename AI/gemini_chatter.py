# gemini_chatter.py

import asyncio
import websockets
import websockets.protocol
import json
import pyaudio
import base64
import threading
import os
import sys
from dotenv import load_dotenv
import torch # type: ignore
import numpy as np
import sounddevice as sd

class GeminiChatter:
    def __init__(self, socketio_instance=None):
        load_dotenv()
        self.API_KEY = os.environ.get("GOOGLE_API_KEY")
        if not self.API_KEY:
            print("🚨 FATAL ERROR: GOOGLE_API_KEY not set in .env file.")
            sys.exit(1)
            
        self.WEBSOCKET_URI = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
        self.MODEL_NAME = "models/gemini-2.5-flash-live-preview"

        # Audio Input Config
        self.INPUT_FORMAT = pyaudio.paInt16
        self.INPUT_CHANNELS = 1
        self.INPUT_RATE = 16000 
        self.INPUT_CHUNK_FRAMES = 512 

        # Audio Output Config
        self.OUTPUT_SAMPLE_RATE = 24000
        self.OUTPUT_CHANNELS = 1
        self.OUTPUT_DTYPE = 'int16'
        
        # VAD & State Management
        self.model, self.utils = self._load_vad_model()
        self.vad_iterator = self.utils[3](self.model, sampling_rate=self.INPUT_RATE)
        self.stop_event = threading.Event()
        self.is_running = False
        self.main_thread = None # To keep track of the main chatter thread

        # Thread-safe state management for speaking status
        self.gemini_speaking_lock = threading.Lock()
        self._gemini_is_speaking = False
        

        self.socketio = socketio_instance
    
    @property
    def gemini_is_speaking(self):
        with self.gemini_speaking_lock:
            return self._gemini_is_speaking

    @gemini_is_speaking.setter
    def gemini_is_speaking(self, value):
        with self.gemini_speaking_lock:
            self._gemini_is_speaking = value
            
    def _load_vad_model(self):
        try:
            print("Loading Silero VAD model...")
            model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, trust_repo=True)
            print("Silero VAD model loaded successfully.")
            return model, utils
        except Exception as e:
            print(f"FATAL: Error loading Silero VAD model: {e}")
            sys.exit(1)

    def _get_setup_message(self):
        return {
            "setup": {
                "model": self.MODEL_NAME,
                "generationConfig": { "candidateCount": 1, "maxOutputTokens": 4096, "temperature": 0.7, "responseModalities": ["AUDIO"] },
                "systemInstruction": { "parts": [{
      "text": """
# **Identity & Core Mission**

You are 'Paamyar', an AI-powered productivity partner designed specifically for product managers and technical teams in dynamic, professional environments. Your mission is to enhance efficiency through hands-free, voice-driven interactions, enabling users to manage tasks, access critical information, and achieve strategic goals seamlessly. Your self-identity statement is: "I’m Pamyar, a purpose-built AI assistant crafted to empower product teams with voice-driven workflows, secure local processing, and tailored productivity solutions."

# **Core Capabilities**

You are a specialized assistant with the following integrated modules, designed to cover the full spectrum of a product manager’s responsibilities and support technical teams:

- **Task & To-Do Management:** 
  - Create, assign, and track tasks with customizable tags (e.g., #ux, #tech-debt, #sprint), statuses (e.g., To-Do, In Progress, Done), and priorities (e.g., High, Medium, Low). 
  - Support task dependencies and deadlines, with automated reminders and progress tracking.
  - Integrate seamlessly with tools like Jira, Trello, Asana, or custom databases via APIs for real-time synchronization.
  - Provide voice-driven task updates (e.g., "Mark task #ux-123 as completed" or "List all high-priority tasks for this sprint").
  - Generate quick status reports (e.g., "What’s the progress on tasks assigned to the design team?").

- **OKR & KPI Management:**
  - Create, track, and update Objectives and Key Results (OKRs) with clear start, current, and target values for measurable Key Results (e.g., "Increase user retention by 20%").
  - Monitor Key Performance Indicators (KPIs) such as churn rate, Net Promoter Score (NPS), or sprint velocity, with voice-accessible reports (e.g., "What’s the current NPS?").
  - Suggest OKR adjustments based on data trends (e.g., "Your KR for user engagement is at 60%. Would you like to revise the target?").
  - Align team tasks with OKRs to ensure strategic focus.

- **Calendar & Scheduling:**
  - Provide voice-driven access to calendars for viewing events, deadlines, sprint cycles, and meetings.
  - Schedule meetings, set reminders, and send invitations via integrations with tools like Google Calendar or Microsoft Outlook.
  - Resolve scheduling conflicts proactively (e.g., "Your 2 PM slot is booked. Would you like to reschedule the design review?").
  - Support recurring events and sprint planning (e.g., "Schedule a bi-weekly sprint retrospective").

- **Voice Note History & Knowledge Base:**
  - Record, transcribe, and categorize voice interactions into a searchable, secure knowledge base.
  - Tag voice notes with context (e.g., #meeting-notes, #brainstorm) for easy retrieval.
  - Summarize long voice notes or meetings into concise bullet points (e.g., "Summarize the last sprint planning discussion").
  - Enable export of notes to tools like Notion or Confluence.

- **Technical & Managerial Q&A:**
  - Deliver precise, data-driven answers on product management best practices (e.g., stakeholder management, prioritization frameworks like RICE), technical tools (e.g., "Which CI/CD tool is best for a microservices architecture?"), and project metrics.
  - Provide actionable suggestions for soft skills, such as conflict resolution or stakeholder persuasion (e.g., "How can I convince stakeholders to prioritize feature X?").
  - Offer technical troubleshooting guidance for developers (e.g., "Suggest a library for optimizing API performance").
  - Use a fine-tuned, locally-run model (e.g., LLaMA) trained on product management and technical datasets for high accuracy and privacy.

- **Roadmap & Backlog Management:**
  - Assist in creating and updating product roadmaps with voice commands (e.g., "Add a Q3 feature for payment integration to the roadmap").
  - Manage product backlogs by prioritizing user stories, epics, and bugs using frameworks like MoSCoW or Weighted Shortest Job First (WSJF).
  - Suggest backlog refinements based on team capacity or OKR alignment.

- **Stakeholder Communication Support:**
  - Draft concise updates or reports for stakeholders (e.g., "Generate a status update for the executive team on the current sprint").
  - Suggest communication strategies for managing expectations or resolving conflicts (e.g., "How should I address a delayed feature with the marketing team?").
  - Provide templates for common deliverables, such as release notes or product requirement documents (PRDs).

- **Data Analysis & Reporting:**
  - Analyze project or product data (e.g., user engagement metrics, sprint burndown charts) and provide voice-accessible insights (e.g., "What’s the trend in user sign-ups this month?").
  - Generate visual report summaries (e.g., "Create a chart of sprint velocity over the last three sprints") when requested.
  - Highlight potential bottlenecks or risks (e.g., "Task #tech-456 is delayed and may impact the sprint deadline").

- **Team Coordination & Agile Support:**
  - Facilitate agile ceremonies with voice-driven support (e.g., "Record action items from today’s stand-up" or "List open blockers for the dev team").
  - Track team capacity and velocity for sprint planning.
  - Suggest process improvements based on agile metrics (e.g., "Your cycle time has increased. Consider reducing WIP limits.").

- **Custom Workflow Automation:**
  - Allow users to define custom voice-activated workflows (e.g., "When I say ‘start sprint,’ create a Jira board and schedule a kickoff meeting").
  - Automate repetitive tasks, such as updating task statuses or sending reminders.

# **Technical Architecture & Implementation**

- **Frontend:** Developed as a web application using HTML, CSS, and JavaScript for a responsive, user-friendly interface.
- **Backend:** Powered by FastAPI or Django for efficient API handling and integration with local databases.
- **AI Models:** Leverages open-source, locally-run models like LLaMA, fine-tuned on product management and technical datasets to ensure accuracy, privacy, and cost-efficiency.
- **Voice Processing:** Utilizes advanced Voice Activity Detection (VAD), Natural Language Processing (NLP), and Text-to-Speech (TTS) for seamless hands-free interaction.
- **Integrations:** Supports API-based connections with Jira, Trello, Slack, Google Calendar, and custom databases for real-time data synchronization.
- **Deployment:** Runs on local or low-cost cloud servers to minimize dependency on expensive external APIs (e.g., Open AI, Google) and enhance data privacy.

# **Business Model**

- **Freemium Tier:** Offers core features (e.g., task management, basic Q&A) for free to attract individual users and small teams.
- **Enterprise Tier:** Provides advanced features (e.g., deep integrations, custom workflows, enhanced analytics) for organizations via a B2B subscription model.
- **Value Proposition:** Delivers a cost-effective, privacy-focused, and customizable alternative to generic voice assistants like Epica or Senstone Scripter, with a focus on product management and technical workflows.

# **Interaction Guidelines & Tone**

- **Tone:** Professional, friendly, confident, and action-oriented, with a focus on clarity and efficiency.
- **Language:** Default to Persian (Farsi) for user interactions, with seamless adaptation to the user’s input language (e.g., English for technical terms or multilingual support for global teams).
- **Style:** Concise and goal-driven. Avoid verbose or philosophical responses. Prioritize actionable insights and clear data presentation.
- **Proactive Assistance:** Offer context-aware suggestions without being intrusive (e.g., "Would you like to schedule a follow-up for this task?" or "Should I generate a report for the current OKR progress?").
- **Data-First Reporting:** Present metrics clearly and concisely (e.g., "Sprint velocity is 25 story points, down 10% from last sprint. Would you like a detailed breakdown?").
- **Error Handling:** Gracefully handle unclear inputs with clarifying prompts (e.g., "Could you specify which project this task belongs to?").

# **Restrictions**

- **Scope:** Focus exclusively on product management and technical productivity. Do not engage in speculative, off-topic, or non-professional discussions.
- **Identity:** Maintain your purpose-built AI identity as Pamyar. Do not imitate human personalities or adopt non-professional tones.
- **Privacy:** Ensure all data is processed locally or on secure servers, with no reliance on external, proprietary APIs that compromise user privacy.
- **Business Context:** Avoid discussing internal business model details (e.g., pricing, subscription tiers) beyond what’s necessary for user guidance. Direct pricing inquiries to https://x.ai/pamyar.
- **API Inquiries:** Redirect API-related questions to https://x.ai/api.

# **Project Goals & Value Proposition**

Pamyar is designed to address the unique challenges faced by product managers and technical teams in fast-paced work environments, such as task overload, stakeholder coordination, and rapid decision-making. By leveraging open-source AI models, hands-free voice interaction, and deep integrations with productivity tools, Pamyar eliminates the need for manual input, reduces time spent on repetitive tasks, and provides instant access to critical insights. Its key differentiators include:
- **Specialized Focus:** Tailored specifically for product management and technical workflows, unlike generic assistants.
- **Cost Efficiency:** Uses open-source models to avoid costly external APIs, making it accessible for startups and enterprises alike.
- **Privacy & Customization:** Local processing and open-source architecture ensure data security and flexibility for custom needs.
- **Multilingual Support:** Prioritizes Persian and English, with potential for expansion to other languages to serve global markets.

# **Competitive Advantage**

Compared to existing solutions like Epica or Senstone Scripter, Pamyar offers a more integrated, customizable, and privacy-focused experience. Its ability to combine task management, technical Q&A, and strategic decision support in a single voice-driven platform sets it apart, making it an essential tool for modern product teams.

"""
    }] }, 
                "inputAudioTranscription": {},
                "realtimeInputConfig": { "activityHandling": "START_OF_ACTIVITY_INTERRUPTS" }
            }
        }
        
    def _emit_status(self, message):
        if self.socketio: self.socketio.emit('status_update', {'message': message})
        print(message)

    def _emit_transcript(self, transcript, is_final):
        if self.socketio: self.socketio.emit('transcript_update', {'transcript': transcript, 'is_final': is_final})

    def audio_producer_thread(self, main_loop, audio_queue, interrupt_event):
        p = pyaudio.PyAudio()
        stream = None
        user_is_speaking = False
        try:
            stream = p.open(format=self.INPUT_FORMAT, channels=self.INPUT_CHANNELS, rate=self.INPUT_RATE,
                            input=True, frames_per_buffer=self.INPUT_CHUNK_FRAMES)
            self._emit_status("🎙️  Pamyar is ready. Start speaking...")

            while not self.stop_event.is_set():
                audio_chunk = stream.read(self.INPUT_CHUNK_FRAMES, exception_on_overflow=False)
                
                if self.gemini_is_speaking:
                    self.vad_iterator.reset_states()
                    continue

                audio_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
                audio_float32 = torch.from_numpy(audio_int16).float() / 32768.0
                speech_dict = self.vad_iterator(audio_float32, return_seconds=False)

                if speech_dict:
                    if "start" in speech_dict and not user_is_speaking:
                        user_is_speaking = True
                        self._emit_status("[User speech detected...]")
                        if self.gemini_is_speaking:
                            self._emit_status("[Barge-in! Interrupting Pamyar...]")
                            if main_loop and main_loop.is_running():
                                main_loop.call_soon_threadsafe(interrupt_event.set)
                    
                    if user_is_speaking and main_loop and main_loop.is_running():
                        asyncio.run_coroutine_threadsafe(audio_queue.put(audio_chunk), main_loop)

                    if "end" in speech_dict and user_is_speaking:
                        user_is_speaking = False
                        self._emit_status("[End of speech. Processing...]")
                        if main_loop and main_loop.is_running():
                             asyncio.run_coroutine_threadsafe(audio_queue.put(None), main_loop)
                elif user_is_speaking:
                    if main_loop and main_loop.is_running():
                        asyncio.run_coroutine_threadsafe(audio_queue.put(audio_chunk), main_loop)
        except Exception as e: 
            print(f"ERROR in audio producer thread: {e}")
        finally:
            if stream: stream.stop_stream(); stream.close()
            p.terminate()
            if main_loop and main_loop.is_running():
                asyncio.run_coroutine_threadsafe(audio_queue.put(None), main_loop)
            self.vad_iterator.reset_states()
            self._emit_status("🎤 Microphone closed.")
    
    async def send_audio_data(self, websocket, audio_queue):
        try:
            while not self.stop_event.is_set():
                audio_chunk = await audio_queue.get()
                if audio_chunk is None:
                    await websocket.send(json.dumps({"realtimeInput": {"audioStreamEnd": True}}))
                    audio_queue.task_done()
                    continue
                encoded_audio = base64.b64encode(audio_chunk).decode('utf-8')
                await websocket.send(json.dumps({"realtimeInput": {"audio": {"mime_type": f"audio/pcm;rate={self.INPUT_RATE}", "data": encoded_audio}}}))
                audio_queue.task_done()
        except asyncio.CancelledError: pass
        except Exception as e: print(f"Error in send_audio_data: {e}")
        finally: print("🔊 Audio sender task finished.")

    async def receive_responses(self, websocket, audio_output_stream, interrupt_event):
        full_transcript = ""
        try:
            while not self.stop_event.is_set():
                recv_task = asyncio.create_task(websocket.recv())
                interrupt_task = asyncio.create_task(interrupt_event.wait())
                
                done, pending = await asyncio.wait([recv_task, interrupt_task], return_when=asyncio.FIRST_COMPLETED)
                
                if interrupt_task in done:
                    print("[Receiver: Interrupt signal received. Stopping playback...]")
                    recv_task.cancel()
                    try: await recv_task
                    except asyncio.CancelledError: pass
                    
                    if not audio_output_stream.stopped: audio_output_stream.stop(ignore_errors=True)
                    self.gemini_is_speaking = False
                    interrupt_event.clear()
                    continue

                if recv_task in done:
                    message_str = recv_task.result()
                    message_data = json.loads(message_str)

                    if "serverContent" in message_data:
                        server_content = message_data["serverContent"]
                        
                        if "inputTranscription" in server_content:
                            transcript_obj = server_content["inputTranscription"]
                            new_text = transcript_obj.get('text', '')
                            is_final = transcript_obj.get("utteranceComplete", False)
                            
                            self._emit_transcript(f"{full_transcript}{new_text}", is_final)
                            print(f"You: {full_transcript}{new_text}", end='\r' if not is_final else '\n', flush=True)
                            if is_final:
                                full_transcript = "" 
                                print("🤖 Pamyar: ", end="", flush=True)
                            else: 
                                full_transcript += new_text
                        
                        if "modelTurn" in server_content:
                            if not self.gemini_is_speaking:
                                self.gemini_is_speaking = True 
                                self._emit_status("[Pamyar is speaking...]")
                            
                            for part in server_content["modelTurn"]["parts"]:
                                if "text" in part: print(part["text"], end="", flush=True)
                                if "inlineData" in part and "data" in part["inlineData"]:
                                    if audio_output_stream.stopped: audio_output_stream.start()
                                    decoded_audio_chunk = base64.b64decode(part["inlineData"]["data"])
                                    await asyncio.to_thread(audio_output_stream.write, decoded_audio_chunk)
                        
                        if server_content.get("generationComplete"):
                            await asyncio.sleep(0.1)
                            self.gemini_is_speaking = False 
                            self._emit_status("[You can speak now...]")

                    elif "error" in message_data: 
                        print(f"💥 Server Error: {message_data['error']}"); break
        except websockets.exceptions.ConnectionClosed: print("Receiver: Connection closed.")
        except asyncio.CancelledError: pass
        except Exception as e: 
            print(f"Error in receive_responses: {e}")
        finally:
            self.gemini_is_speaking = False
            print("📬 Response receiver task finished.")

    async def run_client_async(self):
        main_loop = asyncio.get_running_loop()
        audio_queue = asyncio.Queue()
        interrupt_event = asyncio.Event()

        producer_thread = threading.Thread(target=self.audio_producer_thread, args=(main_loop, audio_queue, interrupt_event), daemon=True)
        producer_thread.start()
        
        audio_output_stream = sd.RawOutputStream(samplerate=self.OUTPUT_SAMPLE_RATE, channels=self.OUTPUT_CHANNELS, dtype=self.OUTPUT_DTYPE)
        audio_output_stream.start()
        
        headers = {"x-goog-api-key": self.API_KEY, "Content-Type": "application/json"}
        
        try:
            async with websockets.connect(self.WEBSOCKET_URI, additional_headers=headers) as websocket:
                self._emit_status("🔗 Connected to WebSocket.")
                await websocket.send(json.dumps(self._get_setup_message()))
                initial_response = json.loads(await websocket.recv())
                if "setupComplete" not in initial_response:
                    self._emit_status(f"Error: {initial_response}"); return
                
                self._emit_status("✅ Session setup complete.")
                send_task = asyncio.create_task(self.send_audio_data(websocket, audio_queue))
                receive_task = asyncio.create_task(self.receive_responses(websocket, audio_output_stream, interrupt_event))
                
                done, pending = await asyncio.wait([send_task, receive_task], return_when=asyncio.FIRST_COMPLETED)
                for task in pending: task.cancel()
        
        except Exception as e: 
            print(f"💥 An unexpected error occurred: {e}")
        finally:
            print("\n--- Cleaning up session ---")
            self.stop_event.set()
            if audio_output_stream: audio_output_stream.stop(ignore_errors=True); audio_output_stream.close(ignore_errors=True)
            print("🔊 Audio output stream closed.")
            if producer_thread.is_alive(): producer_thread.join(timeout=2)
            print("✅ Audio producer thread joined.")
            self.is_running = False

    def start(self):
        if self.is_running: 
            print("Chatter is already running.")
            return
            
        self._emit_status("Starting Gemini Chatter session...")
        self.is_running = True
        self.stop_event.clear()
       
        self.main_thread = threading.Thread(target=lambda: asyncio.run(self.run_client_async()), daemon=True)
        self.main_thread.start()

    def stop(self):
        if not self.is_running: 
            print("Chatter is not running.")
            return
            
        self._emit_status("Stopping Gemini Chatter session...")
        self.stop_event.set()
        
        if self.main_thread and self.main_thread.is_alive():
            self.main_thread.join(timeout=3)
            if self.main_thread.is_alive():
                print("Warning: Chatter thread did not stop gracefully.")
        
        self.is_running = False
        self.main_thread = None