# GraviLog - Smart Risk Analysis Agent

GraviLog is an AI-powered application designed to help pregnant users monitor their health and detect potential pregnancy-related risks early through a conversational interface.

## Features

- **Multilingual Support**: Interact in English or Arabic
- **Proactive Symptom Assessment**: AI asks relevant questions about symptoms
- **Risk Analysis**: Combines rule-based and AI-powered risk assessment
- **Clear Recommendations**: Provides risk level and suggested next steps
- **Doctor Reports**: Generates weekly summaries for healthcare providers

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/gravilog-smart-risk-agent.git
   cd gravilog-smart-risk-agent
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Option 1: Add it to the `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Option 2: Set it as an environment variable:
     ```
     # On Windows
     set OPENAI_API_KEY=your_api_key_here
     # On macOS/Linux
     export OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Use the application:
   - Select your preferred language
   - Answer the symptom-related questions
   - Review your risk assessment and recommendations
   - Generate a report for your doctor if needed

## Application Flow

1. **Language Selection**: Choose between English and Arabic
2. **Symptom Questions**: Answer 3-5 questions about your current symptoms
3. **Risk Assessment**: Receive a risk level (Low/Medium/High) with explanation
4. **Recommendations**: Get clear next steps based on your risk level
5. **Report Generation**: Option to generate a PDF report for your doctor

## Technical Details

- **Frontend**: Streamlit
- **Backend**: Python
- **LLM Integration**: OpenAI API
- **RAG Backend**: LlamaIndex
- **Report Generation**: FPDF, Matplotlib

## Project Structure

```
gravilog-smart-risk-agent/
├── agent/                  # Main application code
│   ├── app.py              # Streamlit application
│   ├── language_handler.py # Language selection and translations
│   ├── symptom_questioner.py # Symptom-related questions
│   ├── risk_analyzer.py    # Risk assessment logic
│   ├── report_generator.py # Report generation
│   └── utils.py            # Utility functions
├── reports/                # Generated reports (created at runtime)
├── patient_data/           # Patient data storage (created at runtime)
├── .env                    # Environment variables
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```




## Acknowledgements

- OpenAI for providing the API for LLM functionality
- LlamaIndex for RAG capabilities
- Streamlit for the web interface
