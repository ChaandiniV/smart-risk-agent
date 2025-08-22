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
                # Severe symptoms that indicate immediate concern - must be explicit
                r"\bsevere\s+headache\b", r"\bblurry\s+vision\b", r"\bspots\s+in\s+vision\b",
                r"\bsevere\s+swelling\b", r"\bsudden\s+swelling\b", r"\bface\s+swelling\b",
                r"\bsevere\s+abdominal\s+pain\b", r"\bconstant\s+abdominal\s+pain\b",
                r"\bdecreased\s+fetal\s+movement\b", r"\bno\s+fetal\s+movement\b", r"\breduced\s+movement\b",
                r"\bvaginal\s+bleeding\b", r"\bfluid\s+leakage\b", r"\bwater\s+breaking\b",
                r"\bfever\s+above\s+38\b", r"\bfever\s+above\s+100\.4\b", r"\bhigh\s+fever\b",
                r"\bdifficulty\s+breathing\b", r"\bshortness\s+of\s+breath\b", r"\bchest\s+pain\b",
                r"\bsevere\s+dizziness\b", r"\bfainting\b", r"\bloss\s+of\s+consciousness\b"
            ],
            "medium_risk_indicators": [
                # Moderate symptoms that need monitoring - must be explicit
                r"\bmild\s+headache\b", r"\boccasional\s+headache\b", r"\bmild\s+swelling\b",
                r"\boccasional\s+abdominal\s+pain\b", r"\bmild\s+abdominal\s+pain\b", r"\bintermittent\s+pain\b",
                r"\bslight\s+change\s+in\s+movement\b", r"\bless\s+active\s+baby\b",
                r"\bmild\s+nausea\b", r"\bincreased\s+nausea\b", r"\bvomiting\b",
                r"\bdizziness\b", r"\bfatigue\b", r"\bextreme\s+fatigue\b",
                r"\bitching\b", r"\brash\b", r"\bskin\s+changes\b"
            ],
            "low_risk_indicators": [
                # Normal or mild symptoms - these should reduce risk
                r"\bno\s+headache\b", r"\bno\s+swelling\b", r"\bnormal\s+vision\b",
                r"\bno\s+abdominal\s+pain\b", r"\bnormal\s+fetal\s+movement\b", r"\bactive\s+baby\b",
                r"\bno\s+bleeding\b", r"\bno\s+unusual\s+symptoms\b", r"\bfeeling\s+well\b",
                r"\bmild\s+discomfort\b", r"\bexpected\s+pregnancy\s+symptoms\b",
                r"\bnormal\s+pregnancy\s+symptoms\b", r"\beverything\s+is\s+fine\b",
                r"\bfeeling\s+good\b", r"\bno\s+problems\b", r"\bnothing\s+severe\b",
                r"\bjust\s+mild\b", r"\bnormal\b", r"\bfine\b"
            ]
        }

    def analyze_risk(self, responses):
        """
        Analyze user responses to determine risk level and provide recommendations.

        Args:
            responses (dict): Dictionary of user responses to symptom questions

        Returns:
            dict: Risk assessment results including:
                - level: "Low", "Medium", or "High"
                - explanation: Explanation of the risk assessment
                - next_steps: Recommended actions
        """
        # First, try rule-based assessment
        rule_based_result = self._rule_based_assessment(responses)

        # Use LLM-based assessment for more nuanced analysis
        llm_result = self._llm_based_assessment(responses)

        # Combine results with more balanced logic
        final_result = self._combine_assessment_results(rule_based_result, llm_result)

        return final_result

    def _rule_based_assessment(self, responses):
        """
        Perform rule-based risk assessment based on clinical guidelines.

        Args:
            responses (dict): Dictionary of user responses to symptom questions

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
        # If user just says "Yes" without specifying severity, don't count as high risk
        simple_yes_responses = 0
        for response in responses.values():
            response_lower = response.lower().strip()
            if response_lower in ["yes", "yes ", "yes."]:
                simple_yes_responses += 1
        
        # If we have simple "Yes" responses but no specific high-risk indicators,
        # reduce the risk count to avoid false positives
        if simple_yes_responses > 0 and high_risk_count == 0:
            # Simple "Yes" responses should not automatically trigger high risk
            # unless combined with specific concerning symptoms
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
        # Give more weight to low-risk indicators to reduce false positives
        if low_risk_count >= 3:
            # If user has multiple low-risk indicators, default to low risk
            return {
                "level": "Low",
                "explanation": "Your responses indicate normal pregnancy symptoms with no concerning signs.",
                "next_steps": "Continue with regular prenatal care and monitoring."
            }
        elif high_risk_count >= 2:
            return {
                "level": "High",
                "explanation": "Multiple high-risk symptoms detected that require immediate medical attention.",
                "next_steps": "Please contact your healthcare provider immediately or go to the emergency room."
            }
        elif high_risk_count == 1 and medium_risk_count >= 1:
            return {
                "level": "High",
                "explanation": "High-risk symptoms combined with additional concerns detected.",
                "next_steps": "Please contact your healthcare provider immediately."
            }
        elif high_risk_count == 1:
            return {
                "level": "Medium",
                "explanation": "One high-risk symptom detected that should be evaluated.",
                "next_steps": "Please contact your healthcare provider within the next 1-2 days."
            }
        elif medium_risk_count >= 2:
            return {
                "level": "Medium",
                "explanation": "Multiple moderate symptoms detected that should be monitored.",
                "next_steps": "Please contact your healthcare provider within the next few days."
            }
        elif medium_risk_count == 1 and low_risk_count >= 1:
            return {
                "level": "Low",
                "explanation": "One moderate symptom detected, but other responses indicate normal pregnancy symptoms.",
                "next_steps": "Continue monitoring and mention this symptom at your next prenatal visit."
            }
        elif medium_risk_count == 1:
            return {
                "level": "Medium",
                "explanation": "One moderate symptom detected that should be monitored.",
                "next_steps": "Please contact your healthcare provider within the next few days."
            }
        else:
            return {
                "level": "Low",
                "explanation": "No concerning symptoms detected. Your responses indicate normal pregnancy symptoms.",
                "next_steps": "Continue with regular prenatal care and monitoring."
            }

    def _llm_based_assessment(self, responses):
        """
        Perform LLM-based risk assessment for more nuanced analysis.

        Args:
            responses (dict): Dictionary of user responses to symptom questions

        Returns:
            dict: LLM-based risk assessment results
        """
        try:
            # Format the responses for the prompt
            formatted_responses = "\n".join([f"Q: {q}\nA: {a}" for q, a in responses.items()])

            # Prepare a more balanced prompt
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
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a prenatal care specialist. Be accurate and balanced in risk assessment. Don't over-diagnose normal pregnancy symptoms."},
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

                # Normalize the risk level
                result["level"] = result["level"].capitalize()
                if result["level"] not in ["Low", "Medium", "High"]:
                    result["level"] = "Low"  # Default to low if unclear

                return result

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing LLM response: {e}")
                # Fallback to a conservative low-risk response
                return {
                    "level": "Low",
                    "explanation": "Unable to determine precise risk level. Defaulting to low risk.",
                    "next_steps": "Please consult with your healthcare provider if you have any concerns."
                }

        except Exception as e:
            print(f"Error in LLM-based assessment: {e}")
            return {
                "level": "Low",
                "explanation": "An error occurred during risk assessment. Defaulting to low risk.",
                "next_steps": "Please consult with your healthcare provider if you have any concerns."
            }

    def _combine_assessment_results(self, rule_based, llm_based):
        """
        Combine rule-based and LLM-based assessment results with balanced logic.

        Args:
            rule_based (dict): Rule-based assessment results
            llm_based (dict): LLM-based assessment results

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
            return {
                "level": "Medium",
                "explanation": f"Conflicting assessments detected. Rule-based: {rule_based['level']}, AI: {llm_based['level']}. Defaulting to medium risk for safety.",
                "next_steps": "Please consult with your healthcare provider to discuss your symptoms."
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
            combined_explanation += f"\n\nNote: AI assessment suggests {secondary_result['level'].lower()} risk."

        return {
            "level": primary_result["level"],
            "explanation": combined_explanation,
            "next_steps": primary_result["next_steps"]
        }
