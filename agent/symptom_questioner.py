import os
from openai import OpenAI

class SymptomQuestioner:
    """
    Handles the generation and management of symptom-related questions
    for pregnant users based on clinical guidelines.
    """

    def __init__(self):
        """Initialize the symptom questioner with predefined questions."""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Predefined questions in English
        self.default_questions_english = [
            "Have you experienced headaches or blurry vision this week?",
            "Have you noticed swelling in your hands, feet, or face?",
            "What was your last recorded blood pressure or glucose level?",
            "Have you felt any unusual abdominal pain or contractions?",
            "Have you noticed any changes in your baby's movement patterns?"
        ]

        # Predefined questions in Arabic
        self.default_questions_arabic = [
            "هل عانيت من صداع أو رؤية ضبابية هذا الأسبوع؟",
            "هل لاحظت تورمًا في يديك أو قدميك أو وجهك؟",
            "ما هو آخر قياس مسجل لضغط الدم أو مستوى السكر في الدم؟",
            "هل شعرت بأي ألم غير عادي في البطن أو تقلصات؟",
            "هل لاحظت أي تغييرات في أنماط حركة طفلك؟"
        ]

    def get_questions(self, language, user_context=None):
        """
        Get a list of relevant symptom questions based on the selected language.

        Args:
            language (str): The selected language ('english' or 'arabic')
            user_context (dict, optional): Additional context about the user
                                          that might help personalize questions

        Returns:
            list: A list of 3-5 relevant symptom questions
        """
        if language == "english":
            return self.default_questions_english
        elif language == "arabic":
            return self.default_questions_arabic
        else:
            # Default to English if language not supported
            return self.default_questions_english

    def generate_personalized_questions(self, language, user_context):
        """
        Generate personalized questions based on user context using LLM.

        Args:
            language (str): The selected language ('english' or 'arabic')
            user_context (dict): Context about the user including:
                - gestational_age: weeks of pregnancy
                - medical_history: relevant medical conditions
                - previous_symptoms: symptoms reported in previous sessions

        Returns:
            list: A list of 3-5 personalized symptom questions
        """
        # Default questions in case LLM generation fails
        default_questions = self.get_questions(language)

        try:
            # Prepare prompt for the LLM
            prompt = self._prepare_question_generation_prompt(language, user_context)

            # Generate questions using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a prenatal care assistant specializing in risk assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Parse the response to extract questions
            generated_content = response.choices[0].message.content
            questions = self._parse_generated_questions(generated_content)

            # Ensure we have at least 3 questions
            if len(questions) < 3:
                # Fill with default questions if needed
                questions.extend(default_questions[:(3 - len(questions))])

            # Limit to 5 questions maximum
            return questions[:5]

        except Exception as e:
            print(f"Error generating personalized questions: {e}")
            return default_questions

    def _prepare_question_generation_prompt(self, language, user_context):
        """Prepare the prompt for question generation."""
        if language == "arabic":
            prompt = f"""
            أنت مساعد رعاية ما قبل الولادة متخصص في تقييم المخاطر. بناءً على المعلومات التالية عن المريضة:
            
            عمر الحمل: {user_context.get('gestational_age', 'غير معروف')} أسبوع
            التاريخ الطبي: {user_context.get('medical_history', 'غير معروف')}
            الأعراض السابقة: {user_context.get('previous_symptoms', 'غير معروف')}
            
            قم بإنشاء 3-5 أسئلة ذات صلة وشخصية لتقييم المخاطر المحتملة المتعلقة بالحمل. يجب أن تكون الأسئلة مباشرة وواضحة ومكتوبة بلغة متعاطفة.
            
            قم بإدراج كل سؤال في سطر منفصل بدون ترقيم أو نقاط.
            """
        else:  # English
            prompt = f"""
            You are a prenatal care assistant specializing in risk assessment. Based on the following information about the patient:
            
            Gestational age: {user_context.get('gestational_age', 'unknown')} weeks
            Medical history: {user_context.get('medical_history', 'unknown')}
            Previous symptoms: {user_context.get('previous_symptoms', 'unknown')}
            
            Create 3-5 relevant and personalized questions to assess potential pregnancy-related risks. Questions should be direct, clear, and written in an empathetic tone.
            
            List each question on a separate line without numbering or bullets.
            """

        return prompt

    def _parse_generated_questions(self, generated_content):
        """Parse the generated content to extract questions."""
        # Split by newlines and filter out empty lines
        lines = [line.strip() for line in generated_content.split('\n') if line.strip()]

        # Filter lines that are likely questions (ending with ? or containing question words)
        questions = [line for line in lines if line.endswith('?') or
                    any(q_word in line.lower() for q_word in ['what', 'how', 'have', 'has', 'do', 'does', 'did', 'is', 'are', 'were', 'was', 'will', 'would', 'could', 'should', 'can'])]

        return questions
