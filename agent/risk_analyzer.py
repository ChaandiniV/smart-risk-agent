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

        # Define clinical rules for risk assessment
        self.clinical_rules = {
            "high_risk_indicators": [
                "severe headache", "blurry vision", "spots in vision",
                "severe swelling", "sudden swelling", "face swelling",
                "blood pressure above 140/90", "systolic above 140", "diastolic above 90",
                "severe abdominal pain", "constant abdominal pain",
                "decreased fetal movement", "no fetal movement", "reduced movement",
                "vaginal bleeding", "fluid leakage", "water breaking",
                "fever above 38", "fever above 100.4", "high fever",
                "difficulty breathing", "shortness of breath", "chest pain"
            ],
            "medium_risk_indicators": [
                "mild headache", "occasional headache", "mild swelling",
                "blood pressure 130-139/80-89", "elevated blood pressure",
                "occasional abdominal pain", "mild abdominal pain", "intermittent pain",
                "slight change in movement", "less active baby",
                "mild nausea", "increased nausea", "vomiting",
                "dizziness", "fatigue", "extreme fatigue",
                "itching", "rash", "skin changes"
            ],
            "low_risk_indicators": [
                "no headache", "no swelling", "normal vision",
                "blood pressure below 130/80", "normal blood pressure",
                "no abdominal pain", "normal fetal movement", "active baby",
                "no bleeding", "no unusual symptoms", "feeling well",
                "mild discomfort", "expected pregnancy symptoms"
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

        # If rule-based assessment is inconclusive or we want more detailed analysis,
        # use LLM-based assessment
        llm_result = self._llm_based_assessment(responses)

        # Combine results, prioritizing higher risk levels
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

        # Check for high risk indicators
        for indicator in self.clinical_rules["high_risk_indicators"]:
            if indicator.lower() in response_text:
                return {
                    "level": "High",
                    "explanation": f"Your responses indicate potential high-risk symptoms including '{indicator}'.",
                    "next_steps": "Please contact your healthcare provider immediately or go to the emergency room."
                }

        # Check for medium risk indicators
        for indicator in self.clinical_rules["medium_risk_indicators"]:
            if indicator.lower() in response_text:
                return {
                    "level": "Medium",
                    "explanation": f"Your responses indicate potential medium-risk symptoms including '{indicator}'.",
                    "next_steps": "Please contact your healthcare provider within the next 1-2 days to discuss these symptoms."
                }

        # Check for blood pressure values
        bp_match = re.search(r'(\d{2,3})[/\\](\d{2,3})', response_text)
        if bp_match:
            systolic = int(bp_match.group(1))
            diastolic = int(bp_match.group(2))

            if systolic >= 140 or diastolic >= 90:
                return {
                    "level": "High",
                    "explanation": f"Your blood pressure reading of {systolic}/{diastolic} is elevated and may indicate hypertension.",
                    "next_steps": "Please contact your healthcare provider immediately to discuss this blood pressure reading."
                }
            elif (systolic >= 130 and systolic < 140) or (diastolic >= 80 and diastolic < 90):
                return {
                    "level": "Medium",
                    "explanation": f"Your blood pressure reading of {systolic}/{diastolic} is slightly elevated.",
                    "next_steps": "Please monitor your blood pressure and contact your healthcare provider within the next few days."
                }

        # If no specific indicators found, default to low risk
        # But we'll let the LLM make the final determination for more nuanced analysis
        return {
            "level": "Low",
            "explanation": "Based on rule-based analysis, no high-risk symptoms were identified.",
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

            # Prepare the prompt
            prompt = f"""
            You are a prenatal care specialist assessing pregnancy-related health risks.
            
            Please analyze the following patient responses to determine their risk level:
            
            {formatted_responses}
            
            Based on these responses, classify the patient's current risk level as "Low", "Medium", or "High".
            
            Provide your assessment in the following JSON format:
            {{
                "level": "Low/Medium/High",
                "explanation": "Detailed explanation of why this risk level was assigned",
                "next_steps": "Recommended actions for the patient"
            }}
            
            For High risk: Recommend immediate medical attention
            For Medium risk: Recommend contacting healthcare provider within 1-2 days
            For Low risk: Recommend continuing regular prenatal care
            
            Only respond with the JSON object, no additional text.
            """

            # Generate assessment using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a prenatal care specialist assessing pregnancy-related health risks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
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
                    result["level"] = "Medium"  # Default to medium if unclear

                return result

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing LLM response: {e}")
                # Fallback to a default response
                return {
                    "level": "Medium",
                    "explanation": "Unable to determine precise risk level. Defaulting to medium risk as a precaution.",
                    "next_steps": "Please consult with your healthcare provider to discuss your symptoms."
                }

        except Exception as e:
            print(f"Error in LLM-based assessment: {e}")
            return {
                "level": "Medium",
                "explanation": "An error occurred during risk assessment. Defaulting to medium risk as a precaution.",
                "next_steps": "Please consult with your healthcare provider to discuss your symptoms."
            }

    def _combine_assessment_results(self, rule_based, llm_based):
        """
        Combine rule-based and LLM-based assessment results.
        Prioritize higher risk levels for safety.

        Args:
            rule_based (dict): Rule-based assessment results
            llm_based (dict): LLM-based assessment results

        Returns:
            dict: Combined assessment results
        """
        risk_levels = {"Low": 1, "Medium": 2, "High": 3}

        # Determine the higher risk level
        if risk_levels[rule_based["level"]] >= risk_levels[llm_based["level"]]:
            primary_result = rule_based
            secondary_result = llm_based
        else:
            primary_result = llm_based
            secondary_result = rule_based

        # Combine explanations if they're different
        combined_explanation = primary_result["explanation"]
        if primary_result["explanation"] != secondary_result["explanation"]:
            combined_explanation += f"\n\nAdditional insight: {secondary_result['explanation']}"

        # Use the next steps from the higher risk assessment
        next_steps = primary_result["next_steps"]

        return {
            "level": primary_result["level"],
            "explanation": combined_explanation,
            "next_steps": next_steps
        }
