import os
from openai import OpenAI
import re

class SymptomQuestioner:
    """
    Handles the generation and management of symptom-related questions
    for pregnant users based on clinical guidelines.
    """

    def __init__(self):
        """Initialize the symptom questioner with predefined questions."""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Predefined questions in English - more specific to avoid false positives
        self.default_questions_english = [
            "Have you experienced any SEVERE headaches, blurry vision, or spots in your vision this week? (Note: mild headaches are common in pregnancy)",
            "Have you noticed SUDDEN or SEVERE swelling in your hands, feet, or face? (Note: mild swelling is normal)",
            "What was your last blood pressure reading? Please provide both numbers (e.g., 120/80) or just the top number if you only know that.",
            "Have you felt any SEVERE or CONSTANT abdominal pain or contractions? (Note: mild discomfort is normal)",
            "Have you noticed any SIGNIFICANT decrease in your baby's movement patterns? (Note: some variation is normal)"
        ]

        # Predefined questions in Arabic - more specific to avoid false positives
        self.default_questions_arabic = [
            "هل عانيت من صداع شديد أو رؤية ضبابية أو بقع في الرؤية هذا الأسبوع؟ (ملاحظة: الصداع الخفيف شائع في الحمل)",
            "هل لاحظت تورمًا مفاجئًا أو شديدًا في يديك أو قدميك أو وجهك؟ (ملاحظة: التورم الخفيف طبيعي)",
            "ما هو آخر قياس لضغط الدم؟ يرجى تقديم الرقمين (مثل 120/80) أو الرقم العلوي فقط إذا كنت تعرفين ذلك فقط.",
            "هل شعرت بأي ألم شديد أو مستمر في البطن أو تقلصات؟ (ملاحظة: الانزعاج الخفيف طبيعي)",
            "هل لاحظت أي انخفاض كبير في أنماط حركة طفلك؟ (ملاحظة: بعض التغييرات طبيعية)"
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
                    {"role": "system", "content": "You are a prenatal care assistant specializing in risk assessment. Generate specific questions that distinguish between normal pregnancy symptoms and concerning symptoms."},
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
        """
        Prepare the prompt for generating personalized questions.

        Args:
            language (str): The selected language
            user_context (dict): User context information

        Returns:
            str: Formatted prompt for question generation
        """
        context_info = ""
        if user_context:
            if "gestational_age" in user_context:
                context_info += f"\n- Gestational age: {user_context['gestational_age']} weeks"
            if "medical_history" in user_context:
                context_info += f"\n- Medical history: {user_context['medical_history']}"
            if "previous_symptoms" in user_context:
                context_info += f"\n- Previous symptoms: {user_context['previous_symptoms']}"

        if language == "english":
            return f"""
            Generate 3-5 specific symptom questions for a pregnant patient based on the following context:
            {context_info}
            
            Guidelines:
            - Focus on symptoms that indicate potential complications
            - Be specific about what constitutes "concerning" vs "normal" symptoms
            - Include blood pressure monitoring questions
            - Consider gestational age-appropriate concerns
            - Use clear, empathetic language
            
            Format each question as a separate line starting with a number.
            """
        else:
            return f"""
            Generate 3-5 specific symptom questions in Arabic for a pregnant patient based on the following context:
            {context_info}
            
            Guidelines:
            - Focus on symptoms that indicate potential complications
            - Be specific about what constitutes "concerning" vs "normal" symptoms
            - Include blood pressure monitoring questions
            - Consider gestational age-appropriate concerns
            - Use clear, empathetic language in Arabic
            
            Format each question as a separate line starting with a number.
            """

    def _parse_generated_questions(self, content):
        """
        Parse generated questions from LLM response.

        Args:
            content (str): Raw content from LLM response

        Returns:
            list: List of parsed questions
        """
        questions = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove numbering and clean up
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering and bullet points
                question = re.sub(r'^\d+\.?\s*', '', line)
                question = re.sub(r'^[-•]\s*', '', question)
                if question:
                    questions.append(question)
        
        return questions
