Minimal Django site scaffold

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## OpenAI Integration for Homework Generation

To enable AI-powered homework generation using OpenAI:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Set the environment variable:
   ```powershell
   $env:OPENAI_API_KEY = "your-api-key-here"
   ```
   Or create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. The system will automatically detect the API key and use OpenAI for generating homework assignments.

If no API key is provided, the system falls back to local template-based generation.

### Features Implemented

✅ **OpenAI API Integration**: Internet-based homework generation using GPT-3.5-turbo
✅ **Intelligent Fallback**: Automatic fallback to local generation if API unavailable
✅ **Status Indicators**: UI shows whether OpenAI or local generation is active
✅ **Educational Prompts**: Context-aware generation for different subjects and difficulty levels
✅ **Quiz Generation**: AI-powered quiz creation with multiple question types
✅ **Quiz Management**: Full CRUD operations for quizzes and questions
✅ **Student Assessment**: Quiz taking and result tracking system

### Testing the Integration

1. Start the Django server: `python manage.py runserver`
2. Navigate to `/teacher/quiz-generator/`
3. Select subject, topic, class level, difficulty, and number of questions
4. Click "Generate Quiz"
5. Review the generated questions and click "Save Quiz"
6. Access quizzes at `/teacher/quizzes/`

### API Key Setup

For production use, set the `OPENAI_API_KEY` environment variable before starting the server:

```powershell
$env:OPENAI_API_KEY = "sk-your-actual-key-here"
python manage.py runserver
```

The system will show "OpenAI включен" when the API is available and properly configured.

### Quiz Features

- **Multiple Question Types**: Single choice, multiple choice, true/false, short answer
- **AI Generation**: Intelligent question creation based on subject and topic
- **Manual Creation**: Create custom quizzes with full control
- **Student Progress**: Track quiz attempts and performance
- **Time Limits**: Optional time restrictions for quiz completion
- **Scoring System**: Automatic scoring with detailed results

Files:
- `mysite/` — project package
- `core/` — example app with a homepage view

Next: Add models, admin, or API endpoints as needed.
