import os
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from openai import OpenAI

class ReportGenerator:
    """
    Generates weekly risk summaries for doctors, including patient responses,
    risk level trends, and suggested follow-up actions.
    """

    def __init__(self):
        """Initialize the report generator."""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Create reports directory if it doesn't exist
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

        # Initialize patient data store (in a real app, this would be a database)
        self.patient_data_dir = Path("patient_data")
        self.patient_data_dir.mkdir(exist_ok=True)

    def generate_report(self, responses, risk_level, risk_explanation, next_steps, language, patient_id="anonymous"):
        """
        Generate a PDF report for the doctor based on the patient's responses and risk assessment.

        Args:
            responses (dict): Dictionary of user responses to symptom questions
            risk_level (str): Assessed risk level ("Low", "Medium", or "High")
            risk_explanation (str): Explanation of the risk assessment
            next_steps (str): Recommended actions
            language (str): The language used in the session
            patient_id (str, optional): Patient identifier. Defaults to "anonymous".

        Returns:
            str: Path to the generated report file
        """
        # Save current session data
        self._save_session_data(patient_id, responses, risk_level, risk_explanation, next_steps)

        # Create PDF report
        report_path = self._create_pdf_report(patient_id, responses, risk_level, risk_explanation, next_steps, language)

        return report_path

    def generate_weekly_summary(self, patient_id, doctor_email=None):
        """
        Generate a weekly summary report for a specific patient.

        Args:
            patient_id (str): Patient identifier
            doctor_email (str, optional): Doctor's email to send the report to

        Returns:
            str: Path to the generated weekly summary report
        """
        # Load patient history
        patient_history = self._load_patient_history(patient_id)

        if not patient_history:
            return None

        # Create weekly summary PDF
        summary_path = self._create_weekly_summary_pdf(patient_id, patient_history)

        # Send email to doctor if email is provided
        if doctor_email:
            self._send_email_to_doctor(doctor_email, summary_path, patient_id)

        return summary_path

    def _save_session_data(self, patient_id, responses, risk_level, risk_explanation, next_steps):
        """Save the current session data for future reference."""
        patient_dir = self.patient_data_dir / patient_id
        patient_dir.mkdir(exist_ok=True)

        # Create a timestamp for the session
        timestamp = datetime.datetime.now().isoformat()

        # Create a session data dictionary
        session_data = {
            "timestamp": timestamp,
            "responses": responses,
            "risk_level": risk_level,
            "risk_explanation": risk_explanation,
            "next_steps": next_steps
        }

        # Save as JSON
        import json
        session_file = patient_dir / f"session_{timestamp.replace(':', '-')}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

    def _load_patient_history(self, patient_id):
        """Load the patient's history from saved session data."""
        patient_dir = self.patient_data_dir / patient_id

        if not patient_dir.exists():
            return []

        # Load all session files
        session_files = list(patient_dir.glob("session_*.json"))

        if not session_files:
            return []

        # Sort by timestamp
        session_files.sort()

        # Load session data
        import json
        history = []
        for file in session_files:
            with open(file, 'r') as f:
                try:
                    session_data = json.load(f)
                    history.append(session_data)
                except json.JSONDecodeError:
                    continue

        return history

    def _create_pdf_report(self, patient_id, responses, risk_level, risk_explanation, next_steps, language):
        """Create a PDF report for the current session."""
        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()

        # Set up fonts
        pdf.set_font("Arial", "B", 16)

        # Title
        pdf.cell(0, 10, "GraviLog - Patient Risk Assessment", ln=True, align="C")
        pdf.ln(5)

        # Patient ID and Date
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Patient ID: {patient_id}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.cell(0, 10, f"Language: {language.capitalize()}", ln=True)
        pdf.ln(5)

        # Risk Level
        risk_colors = {
            "Low": (0, 128, 0),  # Green
            "Medium": (255, 165, 0),  # Orange
            "High": (255, 0, 0)  # Red
        }

        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(*risk_colors.get(risk_level, (0, 0, 0)))
        pdf.cell(0, 10, f"Risk Level: {risk_level}", ln=True)
        pdf.set_text_color(0, 0, 0)  # Reset to black
        pdf.ln(5)

        # Responses
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Patient Responses:", ln=True)
        pdf.set_font("Arial", "", 10)

        for question, answer in responses.items():
            pdf.multi_cell(0, 10, f"Q: {question}\nA: {answer}", border=1)
            pdf.ln(2)

        pdf.ln(5)

        # Risk Explanation
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Risk Explanation:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 10, risk_explanation)
        pdf.ln(5)

        # Next Steps
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recommended Next Steps:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 10, next_steps)

        # Save the PDF
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{patient_id}_report_{timestamp}.pdf"
        report_path = str(self.reports_dir / report_filename)
        pdf.output(report_path)

        return report_path

    def _create_weekly_summary_pdf(self, patient_id, patient_history):
        """Create a weekly summary PDF for the doctor."""
        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()

        # Set up fonts
        pdf.set_font("Arial", "B", 16)

        # Title
        pdf.cell(0, 10, "GraviLog - Weekly Patient Risk Summary", ln=True, align="C")
        pdf.ln(5)

        # Patient ID and Date Range
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Patient ID: {patient_id}", ln=True)

        # Calculate date range
        if patient_history:
            start_date = datetime.datetime.fromisoformat(patient_history[0]["timestamp"]).strftime("%Y-%m-%d")
            end_date = datetime.datetime.fromisoformat(patient_history[-1]["timestamp"]).strftime("%Y-%m-%d")
            pdf.cell(0, 10, f"Date Range: {start_date} to {end_date}", ln=True)

        pdf.ln(5)

        # Risk Level Trend
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Risk Level Trend:", ln=True)

        # Generate risk level trend chart
        if len(patient_history) > 1:
            chart_path = self._generate_risk_trend_chart(patient_history)
            if chart_path:
                pdf.image(chart_path, x=10, y=None, w=180)
                pdf.ln(60)  # Space for the chart

        # Current Risk Level
        if patient_history:
            latest_risk = patient_history[-1]["risk_level"]
            risk_colors = {
                "Low": (0, 128, 0),  # Green
                "Medium": (255, 165, 0),  # Orange
                "High": (255, 0, 0)  # Red
            }

            pdf.set_font("Arial", "B", 14)
            pdf.set_text_color(*risk_colors.get(latest_risk, (0, 0, 0)))
            pdf.cell(0, 10, f"Current Risk Level: {latest_risk}", ln=True)
            pdf.set_text_color(0, 0, 0)  # Reset to black
            pdf.ln(5)

        # Red Flags
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Red Flags:", ln=True)
        pdf.set_font("Arial", "", 10)

        red_flags = self._identify_red_flags(patient_history)
        if red_flags:
            for flag in red_flags:
                pdf.multi_cell(0, 10, f"- {flag}", border=0)
        else:
            pdf.multi_cell(0, 10, "No significant red flags identified.")

        pdf.ln(5)

        # Latest Responses
        if patient_history:
            latest_session = patient_history[-1]
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Latest Patient Responses:", ln=True)
            pdf.set_font("Arial", "", 10)

            for question, answer in latest_session["responses"].items():
                pdf.multi_cell(0, 10, f"Q: {question}\nA: {answer}", border=1)
                pdf.ln(2)

            pdf.ln(5)

        # Suggested Follow-up Actions
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Suggested Follow-up Actions:", ln=True)
        pdf.set_font("Arial", "", 10)

        follow_up_actions = self._generate_follow_up_actions(patient_history)
        pdf.multi_cell(0, 10, follow_up_actions)

        # Save the PDF
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"{patient_id}_weekly_summary_{timestamp}.pdf"
        summary_path = str(self.reports_dir / summary_filename)
        pdf.output(summary_path)

        return summary_path

    def _generate_risk_trend_chart(self, patient_history):
        """Generate a chart showing the risk level trend over time."""
        try:
            # Extract dates and risk levels
            dates = [datetime.datetime.fromisoformat(session["timestamp"]) for session in patient_history]
            risk_levels = [session["risk_level"] for session in patient_history]

            # Convert risk levels to numeric values
            risk_values = {"Low": 1, "Medium": 2, "High": 3}
            numeric_risks = [risk_values.get(level, 0) for level in risk_levels]

            # Create a DataFrame
            df = pd.DataFrame({
                'date': dates,
                'risk': numeric_risks
            })

            # Create the chart
            plt.figure(figsize=(10, 4))
            plt.plot(df['date'], df['risk'], marker='o', linestyle='-', color='blue')
            plt.yticks([1, 2, 3], ['Low', 'Medium', 'High'])
            plt.title('Risk Level Trend')
            plt.xlabel('Date')
            plt.ylabel('Risk Level')
            plt.grid(True)

            # Save the chart
            chart_path = str(self.reports_dir / "temp_chart.png")
            plt.savefig(chart_path)
            plt.close()

            return chart_path

        except Exception as e:
            print(f"Error generating risk trend chart: {e}")
            return None

    def _identify_red_flags(self, patient_history):
        """Identify red flags from the patient's history."""
        red_flags = []

        # Check for persistent high risk
        high_risk_count = sum(1 for session in patient_history if session["risk_level"] == "High")
        if high_risk_count > 0:
            red_flags.append(f"Patient has had {high_risk_count} high risk assessments.")

        # Check for escalating risk
        if len(patient_history) >= 2:
            risk_values = {"Low": 1, "Medium": 2, "High": 3}
            previous_risk = risk_values.get(patient_history[-2]["risk_level"], 0)
            current_risk = risk_values.get(patient_history[-1]["risk_level"], 0)

            if current_risk > previous_risk:
                red_flags.append(f"Risk level has increased from {patient_history[-2]['risk_level']} to {patient_history[-1]['risk_level']}.")

        # Check for specific symptoms in the latest session
        if patient_history:
            latest_responses = " ".join(patient_history[-1]["responses"].values()).lower()

            high_risk_keywords = [
                "severe headache", "blurry vision", "swelling",
                "high blood pressure", "abdominal pain", "decreased movement",
                "bleeding", "fluid", "fever", "difficulty breathing"
            ]

            for keyword in high_risk_keywords:
                if keyword in latest_responses:
                    red_flags.append(f"Patient reported '{keyword}' in the latest session.")

        return red_flags

    def _generate_follow_up_actions(self, patient_history):
        """Generate suggested follow-up actions based on the patient's history."""
        if not patient_history:
            return "No patient history available to generate follow-up actions."

        latest_session = patient_history[-1]
        risk_level = latest_session["risk_level"]

        # Basic follow-up actions based on risk level
        if risk_level == "High":
            return (
                "1. Immediate follow-up appointment recommended within 24 hours.\n"
                "2. Consider referral to specialist or emergency care if symptoms persist.\n"
                "3. Monitor blood pressure and other vital signs closely.\n"
                "4. Review medication regimen and adjust as necessary."
            )
        elif risk_level == "Medium":
            return (
                "1. Schedule follow-up appointment within the next week.\n"
                "2. Request patient to monitor and log symptoms daily.\n"
                "3. Consider additional diagnostic tests if symptoms persist.\n"
                "4. Review dietary and lifestyle recommendations."
            )
        else:  # Low
            return (
                "1. Continue with regular prenatal care schedule.\n"
                "2. Encourage patient to continue using the GraviLog app for monitoring.\n"
                "3. Provide educational resources on normal pregnancy progression.\n"
                "4. Review any concerns at the next scheduled appointment."
            )

    def _send_email_to_doctor(self, doctor_email, report_path, patient_id):
        """Send the report to the doctor via email."""
        # This is a placeholder for email functionality
        # In a real application, you would implement email sending here
        print(f"[Email would be sent to {doctor_email} with report for patient {patient_id}]")
        # The actual implementation would depend on the email service being used
