import os
from openai import OpenAI
import re

class RiskAnalyzer:
    """
    Analyzes user responses to determine pregnancy-related health risks
    and provides recommendations based on clinical guidelines.
    """

    def __init__(self):
        """Initialize the risk analyzer with OpenAI client and clinical rules."""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define clinical rules for risk assessment with more nuanced patterns
        self.clinical_rules = {
            "high_risk_indicators": [
                # English patterns
                r"\bsevere\s+headache\b", r"\bblurry\s+vision\b", r"\bspots\s+in\s+vision\b",
                r"\bsevere\s+swelling\b", r"\bsudden\s+swelling\b", r"\bface\s+swelling\b",
                r"\bsevere\s+abdominal\s+pain\b", r"\bconstant\s+abdominal\s+pain\b",
                r"\bdecreased\s+fetal\s+movement\b", r"\bno\s+fetal\s+movement\b", r"\breduced\s+movement\b",
                r"\bvaginal\s+bleeding\b", r"\bfluid\s+leakage\b", r"\bwater\s+breaking\b",
                r"\bfever\s+above\s+38\b", r"\bfever\s+above\s+100\.4\b", r"\bhigh\s+fever\b",
                r"\bdifficulty\s+breathing\b", r"\bshortness\s+of\s+breath\b", r"\bchest\s+pain\b",
                r"\bsevere\s+dizziness\b", r"\bfainting\b", r"\bloss\s+of\s+consciousness\b",
                # Arabic patterns
                r"\bصداع\s+شديد\b", r"\bرؤية\s+ضبابية\b", r"\bبقع\s+في\s+الرؤية\b",
                r"\bتورم\s+شديد\b", r"\bتورم\s+مفاجئ\b", r"\bتورم\s+الوجه\b",
                r"\bألم\s+شديد\s+في\s+البطن\b", r"\bألم\s+مستمر\s+في\s+البطن\b",
                r"\bانخفاض\s+حركة\s+الجنين\b", r"\bلا\s+حركة\s+للجنين\b", r"\bحركة\s+قليلة\b",
                r"\bنزيف\s+مهبلي\b", r"\bتسرب\s+سائل\b", r"\bانفجار\s+كيس\s+الماء\b",
                r"\bحمى\s+عالية\b", r"\bحمى\s+فوق\s+38\b",
                r"\bصعوبة\s+في\s+التنفس\b", r"\bضيق\s+تنفس\b", r"\bألم\s+في\s+الصدر\b",
                r"\bدوخة\s+شديدة\b", r"\bإغماء\b", r"\bفقدان\s+الوعي\b"
            ],
            "medium_risk_indicators": [
                # English patterns
                r"\bmild\s+headache\b", r"\boccasional\s+headache\b", r"\bmild\s+swelling\b",
                r"\boccasional\s+abdominal\s+pain\b", r"\bmild\s+abdominal\s+pain\b", r"\bintermittent\s+pain\b",
                r"\bslight\s+change\s+in\s+movement\b", r"\bless\s+active\s+baby\b",
                r"\bmild\s+nausea\b", r"\bincreased\s+nausea\b", r"\bvomiting\b",
                r"\bdizziness\b", r"\bfatigue\b", r"\bextreme\s+fatigue\b",
                r"\bitching\b", r"\brash\b", r"\bskin\s+changes\b",
                # Arabic patterns
                r"\bصداع\s+خفيف\b", r"\bصداع\s+أحياناً\b", r"\bتورم\s+خفيف\b",
                r"\bألم\s+خفيف\s+في\s+البطن\b", r"\bألم\s+متقطع\b",
                r"\bتغيير\s+طفيف\s+في\s+الحركة\b", r"\bطفل\s+أقل\s+نشاطاً\b",
                r"\bغثيان\s+خفيف\b", r"\bقيء\b", r"\bدوخة\b", r"\bتعب\b", r"\bحكة\b"
            ],
            "low_risk_indicators": [
                # English patterns
                r"\bno\s+headache\b", r"\bno\s+swelling\b", r"\bnormal\s+vision\b",
                r"\bno\s+abdominal\s+pain\b", r"\bnormal\s+fetal\s+movement\b", r"\bactive\s+baby\b",
                r"\bno\s+bleeding\b", r"\bno\s+unusual\s+symptoms\b", r"\bfeeling\s+well\b",
                r"\bmild\s+discomfort\b", r"\bexpected\s+pregnancy\s+symptoms\b",
                r"\bnormal\s+pregnancy\s+symptoms\b", r"\beverything\s+is\s+fine\b",
                r"\bfeeling\s+good\b", r"\bno\s+problems\b", r"\bnothing\s+severe\b",
                r"\bjust\s+mild\b", r"\bnormal\b", r"\bfine\b",
                # Arabic patterns
                r"\bلا\s+صداع\b", r"\bلا\s+تورم\b", r"\bرؤية\s+طبيعية\b",
                r"\bلا\s+ألم\s+في\s+البطن\b", r"\bحركة\s+الجنين\s+طبيعية\b", r"\bطفل\s+نشيط\b",
                r"\bلا\s+نزيف\b", r"\bلا\s+أعراض\s+غريبة\b", r"\bأشعر\s+بخير\b",
                r"\bكل\s+شيء\s+على\s+ما\s+يرام\b", r"\bأشعر\s+بتحسن\b", r"\bلا\s+مشاكل\b",
                r"\bطبيعي\b", r"\bبخير\b", r"\bلا\s+شيء\s+شديد\b"
            ]
        }
        
        # Translation dictionaries
        self.translations = {
            "english": {
                "high_risk_explanation": "Multiple high-risk symptoms detected that require immediate medical attention.",
                "high_single_explanation": "High-risk symptoms combined with additional concerns detected.",
                "medium_single_explanation": "One high-risk symptom detected that should be evaluated.",
                "medium_multiple_explanation": "Multiple moderate symptoms detected that should be monitored.",
                "low_explanation": "No concerning symptoms detected. Your responses indicate normal pregnancy symptoms.",
                "low_with_mild_explanation": "One moderate symptom detected, but other responses indicate normal pregnancy symptoms.",
                "high_steps": "Please contact your healthcare provider immediately or go to the emergency room.",
                "high_single_steps": "Please contact your healthcare provider immediately.",
                "medium_steps": "Please contact your healthcare provider within the next 1-2 days.",
                "medium_multiple_steps": "Please contact your healthcare provider within the next few days.",
                "low_steps": "Continue with regular prenatal care and monitoring.",
                "low_with_mild_steps": "Continue monitoring and mention this symptom at your next prenatal visit."
            },
            "arabic": {
                "high_risk_explanation": "تم اكتشاف أعراض عالية الخطورة متعددة تتطلب عناية طبية فورية.",
                "high_single_explanation": "تم اكتشاف أعراض عالية الخطورة مع مخاوف إضافية.",
                "medium_single_explanation": "تم اكتشاف عرض واحد عالي الخطورة يجب تقييمه.",
                "medium_multiple_explanation": "تم اكتشاف أعراض متوسطة متعددة يجب مراقبتها.",
                "low_explanation": "لم يتم اكتشاف أعراض مثيرة للقلق. إجاباتك تشير إلى أعراض حمل طبيعية.",
                "low_with_mild_explanation": "تم اكتشاف عرض متوسط واحد، لكن الإجابات الأخرى تشير إلى أعراض حمل طبيعية.",
                "high_steps": "يرجى التواصل مع مقدم الرعاية الصحية فوراً أو الذهاب إلى غرفة الطوارئ.",
                "high_single_steps": "يرجى التواصل مع مقدم الرعاية الصحية فوراً.",
                "medium_steps": "يرجى التواصل مع مقدم الرعاية الصحية خلال الـ1-2 أيام القادمة.",
                "medium_multiple_steps": "يرجى التواصل مع مقدم الرعاية الصحية خلال الأيام القليلة القادمة.",
                "low_steps": "تابعي الرعاية والمتابعة المنتظمة قبل الولادة.",
                "low_with_mild_steps": "تابعي المراقبة واذكري هذا العرض في زيارتك القادمة قبل الولادة."
            }
        }

    def analyze_risk(self, responses, language="english"):
        """
        Analyze user responses to determine risk level and provide recommendations.

        Args:
            responses (dict): Dictionary of user responses to symptom questions
            language (str): Language for responses ("english" or "arabic")

        Returns:
            dict: Risk assessment results including:
                - level: "Low", "Medium", or "High"
                - explanation: Explanation of the risk assessment
                - next_steps: Recommended actions
        """
        # First, try rule-based assessment
        rule_based_result = self._rule_based_assessment(responses, language)

        # Use LLM-based assessment for more nuanced analysis
        llm_result = self._llm_based_assessment(responses, language)

        # Combine results with more balanced logic
        final_result = self._combine_assessment_results(rule_based_result, llm_result, language)

        return final_result

    def _rule_based_assessment(self, responses, language="english"):
        """
        Perform rule-based risk assessment based on clinical guidelines.

        Args:
            responses (dict): Dictionary of user responses to symptom questions
            language (str): Language for responses

        Returns:
            dict: Rule-based risk assessment results
        """
        # Convert all responses to a single string for easier pattern matching
        response_text = " ".join(responses.values()).lower()
        
        # Initialize counters for different risk levels
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0

        # Check for high risk indicators using regex patterns
        for pattern in self.clinical_rules["high_risk_indicators"]:
            if re.search(pattern, response_text, re.IGNORECASE):
                high_risk_count += 1

        # Check for medium risk indicators
        for pattern in self.clinical_rules["medium_risk_indicators"]:
            if re.search(pattern, response_text, re.IGNORECASE):
                medium_risk_count += 1

        # Check for low risk indicators
        for pattern in self.clinical_rules["low_risk_indicators"]:
            if re.search(pattern, response_text, re.IGNORECASE):
                low_risk_count += 1

        # Check for simple "Yes" responses that might be false positives
        simple_yes_responses = 0
        for response in responses.values():
            response_lower = response.lower().strip()
            if response_lower in ["yes", "yes ", "yes.", "نعم", "اجل", "موافق"]:
                simple_yes_responses += 1
        
        # If we have simple "Yes" responses but no specific high-risk indicators,
        # reduce the risk count to avoid false positives
        if simple_yes_responses > 0 and high_risk_count == 0:
            high_risk_count = 0
            medium_risk_count = max(0, medium_risk_count - simple_yes_responses)

        # Check for blood pressure values with more flexible parsing
        bp_patterns = [
            r'(\d{2,3})[/\\](\d{2,3})',  # 160/90 format
            r'(\d{2,3})\s*over\s*(\d{2,3})',  # 160 over 90 format
            r'(\d{2,3})\s*(\d{2,3})',  # 160 90 format
        ]
        
        for pattern in bp_patterns:
            bp_match = re.search(pattern, response_text)
            if bp_match:
                systolic = int(bp_match.group(1))
                diastolic = int(bp_match.group(2))

                if systolic >= 140 or diastolic >= 90:
                    high_risk_count += 2  # Give extra weight to high BP
                elif (systolic >= 130 and systolic < 140) or (diastolic >= 80 and diastolic < 90):
                    medium_risk_count += 1
                break

        # Check for single blood pressure numbers (systolic only)
        single_bp_match = re.search(r'\b(\d{2,3})\b', response_text)
        if single_bp_match:
            bp_value = int(single_bp_match.group(1))
            if bp_value >= 140:
                high_risk_count += 1
            elif bp_value >= 130:
                medium_risk_count += 1

        # Determine risk level based on counts and context
        return self._determine_risk_level(high_risk_count, medium_risk_count, low_risk_count, language)

    def _determine_risk_level(self, high_risk_count, medium_risk_count, low_risk_count, language):
        """Determine risk level based on symptom counts."""
        trans = self.translations[language]
        
        # Give more weight to low-risk indicators to reduce false positives
        if low_risk_count >= 3:
            return {
                "level": "Low",
                "explanation": trans["low_explanation"],
                "next_steps": trans["low_steps"]
            }
        elif high_risk_count >= 2:
            return {
                "level": "High",
                "explanation": trans["high_risk_explanation"],
                "next_steps": trans["high_steps"]
            }
        elif high_risk_count == 1 and medium_risk_count >= 1:
            return {
                "level": "High",
                "explanation": trans["high_single_explanation"],
                "next_steps": trans["high_single_steps"]
            }
        elif high_risk_count == 1:
            return {
                "level": "Medium",
                "explanation": trans["medium_single_explanation"],
                "next_steps": trans["medium_steps"]
            }
        elif medium_risk_count >= 2:
            return {
                "level": "Medium",
                "explanation": trans["medium_multiple_explanation"],
                "next_steps": trans["medium_multiple_steps"]
            }
        elif medium_risk_count == 1 and low_risk_count >= 1:
            return {
                "level": "Low",
                "explanation": trans["low_with_mild_explanation"],
                "next_steps": trans["low_with_mild_steps"]
            }
        elif medium_risk_count == 1:
            return {
                "level": "Medium",
                "explanation": trans["medium_single_explanation"],
                "next_steps": trans["medium_steps"]
            }
        else:
            return {
                "level": "Low",
                "explanation": trans["low_explanation"],
                "next_steps": trans["low_steps"]
            }

    def _llm_based_assessment(self, responses, language="english"):
        """
        Perform LLM-based risk assessment for more nuanced analysis.

        Args:
            responses (dict): Dictionary of user responses to symptom questions
            language (str): Language for responses

        Returns:
            dict: LLM-based risk assessment results
        """
        try:
            # Format the responses for the prompt
            formatted_responses = "\n".join([f"Q: {q}\nA: {a}" for q, a in responses.items()])

            # Prepare language-specific prompt
            if language == "arabic":
                prompt = f"""
                أنت أخصائي رعاية ما قبل الولادة تقوم بتقييم المخاطر الصحية المتعلقة بالحمل.
                
                حلل إجابات المريضة التالية لتحديد مستوى المخاطر لديها:
                
                {formatted_responses}
                
                إرشادات مهمة:
                - إجابة "نعم" بسيطة بدون سياق يجب ألا تؤدي تلقائياً لخطر عالي
                - صنف كـ "مرتفع" فقط إذا كانت هناك علامات واضحة لمضاعفات خطيرة:
                  * أعراض شديدة مذكورة صراحة (صداع شديد، تورم شديد، إلخ)
                  * أعراض مثيرة للقلق متعددة معاً
                  * قيم خطيرة محددة (ضغط الدم ≥140/90، إلخ)
                - صنف كـ "متوسط" لـ:
                  * ارتفاع ضغط الدم (130-139/80-89)
                  * أعراض متوسطة مفردة تحتاج مراقبة
                - صنف كـ "منخفض" لـ:
                  * أعراض الحمل الطبيعية
                  * انزعاج خفيف
                  * إجابات تشير أن كل شيء بخير
                  * إجابات "نعم" بسيطة بدون سياق خطورة
                - كن محافظاً لكن دقيقاً - لا تفرط في تشخيص أعراض الحمل الطبيعية
                
                قدم تقييمك بتنسيق JSON التالي:
                {{
                    "level": "منخفض/متوسط/مرتفع",
                    "explanation": "تفسير واضح لسبب تحديد مستوى الخطر هذا",
                    "next_steps": "الإجراءات الموصى بها تحديداً"
                }}
                
                أجب بكائن JSON فقط، بدون نص إضافي.
                """
            else:
                prompt = f"""
                You are a prenatal care specialist assessing pregnancy-related health risks.
                
                Analyze the following patient responses to determine their risk level:
                
                {formatted_responses}
                
                CRITICAL GUIDELINES:
                - A simple "Yes" response without context should NOT automatically trigger high risk
                - Only classify as "High" risk if there are CLEAR signs of serious complications:
                  * Severe symptoms explicitly mentioned (severe headache, severe swelling, etc.)
                  * Multiple concerning symptoms together
                  * Specific dangerous values (BP ≥140/90, etc.)
                - Classify as "Medium" risk for:
                  * Elevated blood pressure (130-139/80-89)
                  * Single moderate symptoms that need monitoring
                - Classify as "Low" risk for:
                  * Normal pregnancy symptoms
                  * Mild discomfort
                  * Responses indicating everything is fine
                  * Simple "Yes" responses without severity context
                - Be conservative but accurate - don't over-diagnose normal pregnancy symptoms
                
                Provide your assessment in the following JSON format:
                {{
                    "level": "Low/Medium/High",
                    "explanation": "Clear explanation of why this risk level was assigned",
                    "next_steps": "Specific recommended actions"
                }}
                
                Only respond with the JSON object, no additional text.
                """

            # Generate assessment using OpenAI with lower temperature for more consistent results
            system_message = "أنت أخصائي رعاية ما قبل الولادة. كن دقيقاً ومتوازناً في تقييم المخاطر. لا تفرط في تشخيص أعراض الحمل الطبيعية." if language == "arabic" else "You are a prenatal care specialist. Be accurate and balanced in risk assessment. Don't over-diagnose normal pregnancy symptoms."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent results
                max_tokens=300
            )

            # Extract and parse the response
            result_text = response.choices[0].message.content.strip()

            # Try to extract JSON from the response
            import json
            try:
                # Find JSON object in the response if there's additional text
                json_match = re.search(r'({.*})', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)

                result = json.loads(result_text)

                # Ensure the result has the required fields
                if not all(key in result for key in ["level", "explanation", "next_steps"]):
                    raise ValueError("Missing required fields in LLM response")

                # Normalize the risk level for both languages
                if language == "arabic":
                    level_mapping = {"منخفض": "Low", "متوسط": "Medium", "مرتفع": "High"}
                    result["level"] = level_mapping.get(result["level"], "Low")
                else:
                    result["level"] = result["level"].capitalize()
                    if result["level"] not in ["Low", "Medium", "High"]:
                        result["level"] = "Low"  # Default to low if unclear

                return result

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing LLM response: {e}")
                # Fallback to a conservative low-risk response
                trans = self.translations[language]
                return {
                    "level": "Low",
                    "explanation": trans["low_explanation"],
                    "next_steps": trans["low_steps"]
                }

        except Exception as e:
            print(f"Error in LLM-based assessment: {e}")
            trans = self.translations[language]
            return {
                "level": "Low",
                "explanation": trans["low_explanation"],
                "next_steps": trans["low_steps"]
            }

    def _combine_assessment_results(self, rule_based, llm_based, language="english"):
        """
        Combine rule-based and LLM-based assessment results with balanced logic.

        Args:
            rule_based (dict): Rule-based assessment results
            llm_based (dict): LLM-based assessment results
            language (str): Language for responses

        Returns:
            dict: Combined assessment results
        """
        risk_levels = {"Low": 1, "Medium": 2, "High": 3}

        # If both assessments agree, use that result
        if rule_based["level"] == llm_based["level"]:
            return rule_based

        # If one is High and the other is Low, default to Medium for safety
        if (rule_based["level"] == "High" and llm_based["level"] == "Low") or \
           (rule_based["level"] == "Low" and llm_based["level"] == "High"):
            
            if language == "arabic":
                explanation = f"تم اكتشاف تقييمات متضاربة. التقييم القائم على القواعد: {rule_based['level']}، الذكاء الاصطناعي: {llm_based['level']}. التعيين للخطر المتوسط للأمان."
                next_steps = "يرجى استشارة مقدم الرعاية الصحية لمناقشة أعراضك."
            else:
                explanation = f"Conflicting assessments detected. Rule-based: {rule_based['level']}, AI: {llm_based['level']}. Defaulting to medium risk for safety."
                next_steps = "Please consult with your healthcare provider to discuss your symptoms."
                
            return {
                "level": "Medium",
                "explanation": explanation,
                "next_steps": next_steps
            }

        # For other combinations, use the higher risk level but with explanation
        if risk_levels[rule_based["level"]] > risk_levels[llm_based["level"]]:
            primary_result = rule_based
            secondary_result = llm_based
        else:
            primary_result = llm_based
            secondary_result = rule_based

        # Combine explanations
        combined_explanation = primary_result["explanation"]
        if primary_result["explanation"] != secondary_result["explanation"]:
            if language == "arabic":
                combined_explanation += f"\n\nملاحظة: تقييم الذكاء الاصطناعي يشير إلى خطر {secondary_result['level'].lower()}."
            else:
                combined_explanation += f"\n\nNote: AI assessment suggests {secondary_result['level'].lower()} risk."

        return {
            "level": primary_result["level"],
            "explanation": combined_explanation,
            "next_steps": primary_result["next_steps"]
        }
