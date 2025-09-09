class LanguageHandler:
    """
    Handles language selection and translations for the GraviLog application.
    Currently supports English and Arabic with comprehensive translations.
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
                },
                "input_placeholder": "Type your reply...",
                "language_prompt": "Please choose either English or Arabic.",
                "yes_responses": ["yes", "yeah", "yep", "sure", "ok", "okay"],
                "no_responses": ["no", "nope", "not really", "nah"]
            },
            "arabic": {
                "greeting": "ما هي اللغة التي تفضلين أن أستخدمها؟",
                "introduction": "مرحباً! سأطرح عليك بعض الأسئلة البسيطة للمساعدة في تقييم حالتك الصحية.",
                "placeholder": "اكتبي إجابتك هنا...",
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
                },
                "input_placeholder": "اكتبي ردك هنا...",
                "language_prompt": "يرجى الاختيار بين الإنجليزية أو العربية.",
                "yes_responses": ["نعم", "اجل", "موافق", "حسناً", "اوكي", "تمام"],
                "no_responses": ["لا", "كلا", "ليس حقاً", "لا أريد"]
            }
        }

        # Language detection patterns
        self.language_patterns = {
            "english": ["eng", "english", "انجليزية", "إنجليزية"],
            "arabic": ["ara", "arabic", "عربية", "العربية", "عرب"]
        }

    def get_greeting(self):
        """Return the initial greeting asking for language preference."""
        return "Hello! Before we begin, would you like to continue in **English** or **Arabic**? \n\nمرحباً! قبل أن نبدأ، هل تريدين المتابعة باللغة **الإنجليزية** أم **العربية**؟"

    def get_introduction(self, language):
        """Return the introduction text in the selected language."""
        return self.translations[language]["introduction"]

    def get_placeholder(self, language):
        """Return the placeholder text for input fields."""
        return self.translations[language]["placeholder"]

    def get_input_placeholder(self, language):
        """Return the input placeholder text."""
        return self.translations[language]["input_placeholder"]

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

    def get_language_prompt(self, language):
        """Return the language selection prompt."""
        return self.translations[language]["language_prompt"]

    def detect_language_choice(self, user_input):
        """
        Detect language choice from user input.
        
        Args:
            user_input (str): User's input text
            
        Returns:
            str or None: "english", "arabic", or None if no clear choice
        """
        user_input_lower = user_input.lower().strip()
        
        # Check for English patterns
        for pattern in self.language_patterns["english"]:
            if pattern in user_input_lower:
                return "english"
        
        # Check for Arabic patterns  
        for pattern in self.language_patterns["arabic"]:
            if pattern in user_input_lower:
                return "arabic"
                
        return None

    def is_affirmative_response(self, user_input, language):
        """
        Check if user input is an affirmative response.
        
        Args:
            user_input (str): User's input text
            language (str): Current language
            
        Returns:
            bool: True if affirmative, False otherwise
        """
        user_input_lower = user_input.lower().strip()
        
        yes_responses = self.translations[language]["yes_responses"]
        
        return any(word in user_input_lower for word in yes_responses)

    def is_negative_response(self, user_input, language):
        """
        Check if user input is a negative response.
        
        Args:
            user_input (str): User's input text
            language (str): Current language
            
        Returns:
            bool: True if negative, False otherwise
        """
        user_input_lower = user_input.lower().strip()
        
        no_responses = self.translations[language]["no_responses"]
        
        return any(word in user_input_lower for word in no_responses)

    def get_goodbye_message(self, language):
        """Return appropriate goodbye message."""
        if language == "english":
            return "Okay! You can start over anytime by refreshing the app."
        else:
            return "حسناً! يمكنك البدء من جديد في أي وقت عن طريق تحديث التطبيق."

    def get_footer_text(self, language):
        """Return footer text in the appropriate language."""
        if language == "english":
            return "© 2025 GraviLog - Smart Risk Analysis for Pregnancy"
        else:
            return "© 2025 GraviLog - تحليل المخاطر الذكي للحمل"
