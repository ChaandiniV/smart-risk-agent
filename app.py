import os

import streamlit as st
from dotenv import load_dotenv

from agent.language_handler import LanguageHandler
from agent.report_generator import ReportGenerator
from agent.risk_analyzer import RiskAnalyzer
from agent.symptom_questioner import SymptomQuestioner

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

st.markdown(
    """
    <style>
      :root { --bg:#0b0f14; --panel:#0f172a; --border:#1f2937; --fg:#e5e7eb; --fg-dim:#94a3b8; --g1:#4cc3ff; --g2:#ff65a3; }
      body { background: var(--bg); }
      /* Add generous top padding so header never clips under Streamlit chrome */
      .block-container { max-width: 920px; padding-top: 56px; padding-bottom: 7.5rem; }

      /* Product wordmark header */
      .gl-hero { text-align:center; margin: 12px 0 12px; }
      .gl-wordmark { font-weight: 800; font-size: 28px; letter-spacing: 0.3px; background: linear-gradient(90deg, var(--g1), var(--g2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
      .gl-tagline { color: var(--fg-dim); font-size: 13px; margin-top: 4px; }

      /* Chat bubbles */
      .gl-msg { margin: 8px 0; }
      .gl-assistant { background: rgba(30,41,59,.6); border:1px solid var(--border); color: var(--fg); border-radius: 12px; padding: 14px 16px; }
      .gl-user { background: rgba(37,99,235,.12); border:1px solid rgba(37,99,235,.35); color:#dbeafe; border-radius: 12px; padding: 14px 16px; }
      .gl-assistant a, .gl-user a { color:#60a5fa; }

      /* Footer just above input bar */
      .gl-footer { position: fixed; left:0; right:0; bottom: 52px; text-align:center; color: var(--fg-dim); font-size: 12px; padding: 4px; }
      @media (max-width:640px){ .block-container { padding-bottom: 8.5rem; } .gl-footer { bottom: 60px; } }
    </style>
    """,
    unsafe_allow_html=True,
)

# Wordmark header (no external logo)
st.markdown("<div class='gl-hero'><div class='gl-wordmark'>GraviLog</div><div class='gl-tagline'>Smart Risk Analysis for Pregnancy</div></div>", unsafe_allow_html=True)


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

# Display chat history (styled bubbles)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        klass = "gl-assistant" if msg["role"] == "assistant" else "gl-user"
        st.markdown(f"<div class='gl-msg {klass}'>" + msg["content"].replace("\n","\n\n") + "</div>", unsafe_allow_html=True)

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

# Footer beneath input bar (fixed)
st.markdown("<div class='gl-footer'>© 2025 GraviLog - Smart Risk Analysis for Pregnancy</div>", unsafe_allow_html=True)
