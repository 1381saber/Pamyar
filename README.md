# Pamyar

Pamyar is an intelligent voice assistant designed to enhance productivity for product managers and technical teams. Built with a focus on seamless voice interaction, task management, and integration with popular project management tools like Jira and Trello, Pamyar streamlines workflows in fast-paced work environments. With support for Persian and English, it addresses the needs of multilingual users while leveraging open-source AI models to ensure cost-efficiency and data privacy.

## Features

- **Voice-Based Task Management**: Create, edit, and prioritize tasks using natural voice commands, reducing manual input and saving time during meetings.
- **Real-Time Meeting Summarization**: Automatically transcribe and summarize meeting content using advanced NLP, allowing users to focus on discussions.
- **Specialized Query Responses**: Answer technical and managerial queries (e.g., API optimization, sprint status) with precise, context-aware responses powered by LLaMA.
- **Multi-Language Support**: Process commands and responses in Persian and English, catering to diverse user bases.
- **Tool Integrations**: Seamlessly connect with Jira, Trello, and Google Calendar for task synchronization and reminders.
- **OKR Management**: Define and track long-term objectives and key results to align team efforts with project goals.
- **Secure and Scalable**: Built with Django and PostgreSQL for robust data management, AES-256 encryption for security, and Docker for scalable deployment.
- **Offline Capabilities**: Handle basic voice commands offline using local models (planned for future releases).

## Tech Stack

- **Frontend**: HTML5, CSS3 (Tailwind), JavaScript (ES6+), Socket.IO for real-time interaction.
- **Backend**: Django 4.2 (REST APIs, JWT authentication), Flask 2.3 (voice and text processing).
- **AI Pipeline**: 
  - Speech-to-Text: Whisper (with Persian support).
  - Voice Activity Detection: Silero VAD.
  - NLP: LLaMA for query processing and response generation.
- **Database**: PostgreSQL (production), SQLite (development).
- **Other**: Celery (task queue), Redis (message broker), PyAudio (audio capture).

## Installation

### Prerequisites
- Python 3.9+

### Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/pamyar.git
   cd pamyar
   ```

2. **Backend Setup (Django)**:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Voice Processing (Flask)**:
   ```bash
   cd voice_server
   pip install -r requirements.txt
   python app.py
   ```

4. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **Docker (Optional)**:
   ```bash
   docker-compose up --build
   ```

## Usage

1. **Register/Login**: Access the web interface at `http://localhost:8000` to create an account or log in.
2. **Voice Commands**: Use the `/listening` page to issue voice commands like "Add a task to review API documentation" or "Summarize today's meeting."
3. **Text Queries**: Use the `/chatbot` page to ask technical or managerial questions, e.g., "How to optimize a REST API?"
4. **Integrations**: Configure Jira/Trello API keys in the settings to sync tasks and projects.
5. **OKR Tracking**: Define objectives and key results in the `/objectives` page to monitor progress.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the UI License.

## Contact

For questions or feedback, reach out via sabersabzi2002@gmail.com or open an issue on GitHub.
