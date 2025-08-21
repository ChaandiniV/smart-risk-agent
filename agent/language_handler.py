class LanguageHandler:
    """
    Handles language selection and translations for the GraviLog application.
    Currently supports English and Arabic.
    """

    def __init__(self):
        """Initialize the language handler with translations."""
        self.translations = {
            "english": {
                "greeting": "What language would you prefer I use?",
                "introduction": "Hello! I'll ask you a few simple questions to help assess your health condition.",
                "placeholder": "Type your answer here...",
                "submit_button": "Submit",
                "result_header": "Risk Assessment Results",
                "risk_level_text": "Current risk level",
                "explanation_header": "Explanation",
                "next_steps_header": "Recommended Next Steps",
                "generate_report": "Generate Report for Doctor",
                "report_success": "Report generated successfully!",
                "download_report": "Download Report",
                "start_over": "Start Over",
                "risk_levels": {
                    "Low": "Low",
                    "Medium": "Medium",
                    "High": "High"
                }
            },
            "arabic": {
                "greeting": "ما هي اللغة التي تفضل أن أستخدمها؟",
                "introduction": "مرحبًا! سأطرح عليك بعض الأسئلة البسيطة للمساعدة في تقييم حالتك الصحية.",
                "placeholder": "اكتب إجابتك هنا...",
                "submit_button": "إرسال",
                "result_header": "نتائج تقييم المخاطر",
                "risk_level_text": "مستوى الخطر الحالي",
                "explanation_header": "التفسير",
                "next_steps_header": "الخطوات التالية الموصى بها",
                "generate_report": "إنشاء تقرير للطبيب",
                "report_success": "تم إنشاء التقرير بنجاح!",
                "download_report": "تنزيل التقرير",
                "start_over": "البدء من جديد",
                "risk_levels": {
                    "Low": "منخفض",
                    "Medium": "متوسط",
                    "High": "مرتفع"
                }
            }
        }

    def get_greeting(self):
        """Return the initial greeting asking for language preference."""
        return "What language would you prefer I use?"

    def get_introduction(self, language):
        """Return the introduction text in the selected language."""
        return self.translations[language]["introduction"]

    def get_placeholder(self, language):
        """Return the placeholder text for input fields."""
        return self.translations[language]["placeholder"]

    def get_submit_button_text(self, language):
        """Return the submit button text."""
        return self.translations[language]["submit_button"]

    def get_result_header(self, language):
        """Return the result header text."""
        return self.translations[language]["result_header"]

    def get_risk_level_text(self, language):
        """Return the risk level label text."""
        return self.translations[language]["risk_level_text"]

    def translate_risk_level(self, risk_level, language):
        """Translate the risk level to the selected language."""
        return self.translations[language]["risk_levels"][risk_level]

    def get_explanation_header(self, language):
        """Return the explanation header text."""
        return self.translations[language]["explanation_header"]

    def get_next_steps_header(self, language):
        """Return the next steps header text."""
        return self.translations[language]["next_steps_header"]

    def get_generate_report_text(self, language):
        """Return the generate report button text."""
        return self.translations[language]["generate_report"]

    def get_report_success_message(self, language):
        """Return the report success message."""
        return self.translations[language]["report_success"]

    def get_download_report_text(self, language):
        """Return the download report link text."""
        return self.translations[language]["download_report"]

    def get_start_over_text(self, language):
        """Return the start over button text."""
        return self.translations[language]["start_over"]
