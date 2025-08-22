import streamlit as st
import os
from dotenv import load_dotenv
from language_handler import LanguageHandler
from symptom_questioner import SymptomQuestioner
from risk_analyzer import RiskAnalyzer
from report_generator import ReportGenerator

# Load environment variables
load_dotenv()

# Check if OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found in environment variables. Please set it up.")
    st.stop()

# Page config
st.set_page_config(
    page_title="GraviLog - Smart Risk Analysis",
    page_icon="👶",
    layout="centered"
)

# Initialize components
language_handler = LanguageHandler()
symptom_questioner = SymptomQuestioner()
risk_analyzer = RiskAnalyzer()
report_generator = ReportGenerator()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = None
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "risk_result" not in st.session_state:
    st.session_state.risk_result = None
if "report_path" not in st.session_state:
    st.session_state.report_path = None
if "show_download" not in st.session_state:
    st.session_state.show_download = False


# Helper to add assistant messages
def add_assistant_message(content):
    st.session_state.messages.append({"role": "assistant", "content": content})


# Helper to add user messages
def add_user_message(content):
    st.session_state.messages.append({"role": "user", "content": content})


# 1. Start the conversation
if not st.session_state.language:
    if len(st.session_state.messages) == 0:
        add_assistant_message("Hello! Before we begin, would you like to continue in **English** or **Arabic**?")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Show download button if report is ready
if st.session_state.show_download and st.session_state.report_path:
    import os
    if os.path.exists(st.session_state.report_path):
        with open(st.session_state.report_path, "rb") as file:
            st.download_button(
                label="📄 Download Report PDF",
                data=file.read(),
                file_name=os.path.basename(st.session_state.report_path),
                mime="application/pdf"
            )

# Input box
if prompt := st.chat_input("Type your reply..."):

    # Case 1: Language selection
    if st.session_state.language is None:
        add_user_message(prompt)

        if prompt.strip().lower().startswith("eng"):
            st.session_state.language = "english"
            add_assistant_message(language_handler.get_introduction("english"))
            st.session_state.questions = symptom_questioner.get_questions("english")

        elif prompt.strip().lower().startswith("ara"):
            st.session_state.language = "arabic"
            add_assistant_message(language_handler.get_introduction("arabic"))
            st.session_state.questions = symptom_questioner.get_questions("arabic")

        else:
            add_assistant_message("Please choose either English or Arabic.")

    # Case 2: Symptom questioning
    elif st.session_state.risk_result is None and st.session_state.current_q_index < len(st.session_state.questions):
        current_q = st.session_state.questions[st.session_state.current_q_index]
        add_user_message(prompt)
        st.session_state.responses[current_q] = prompt
        st.session_state.current_q_index += 1

        # Ask next question or move to risk analysis
        if st.session_state.current_q_index < len(st.session_state.questions):
            next_q = st.session_state.questions[st.session_state.current_q_index]
            add_assistant_message(next_q)
        else:
            # Analyze risk
            risk_result = risk_analyzer.analyze_risk(st.session_state.responses)
            st.session_state.risk_result = risk_result

            risk_color = {
                "Low": "🟢",
                "Medium": "🟠",
                "High": "🔴"
            }
            add_assistant_message(
                f"**Current risk level:** {risk_color[risk_result['level']]} {risk_result['level']}\n\n"
                f"**Explanation:** {risk_result['explanation']}\n\n"
                f"**Next Steps:** {risk_result['next_steps']}"
            )
            add_assistant_message("Would you like me to generate a report PDF for your doctor?")

    # Case 3: After risk result (PDF step)
    elif st.session_state.risk_result is not None:
        add_user_message(prompt)

        if "yes" in prompt.lower():
            report_path = report_generator.generate_report(
                st.session_state.responses,
                st.session_state.risk_result["level"],
                st.session_state.risk_result["explanation"],
                st.session_state.risk_result["next_steps"],
                st.session_state.language
            )
            add_assistant_message("✅ Report generated successfully!")
            
            # Store the report path in session state for download button
            st.session_state.report_path = report_path
            st.session_state.show_download = True
        else:
            add_assistant_message("Okay! You can start over anytime by refreshing the app.")
            # Reset download state
            st.session_state.show_download = False
            st.session_state.report_path = None

    st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2025 GraviLog - Smart Risk Analysis for Pregnancy")
