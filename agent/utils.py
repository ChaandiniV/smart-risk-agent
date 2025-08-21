import re
import os
import json
from datetime import datetime
from pathlib import Path

class Utils:
    """
    Utility functions for the GraviLog application.
    """

    @staticmethod
    def validate_blood_pressure(bp_text):
        """
        Validate and parse blood pressure readings from text.

        Args:
            bp_text (str): Text containing blood pressure reading

        Returns:
            tuple: (systolic, diastolic) or (None, None) if invalid
        """
        if not bp_text:
            return None, None

        # Look for patterns like "120/80", "120-80", "120 / 80"
        bp_pattern = re.compile(r'(\d{2,3})\s*[/\\-]\s*(\d{2,3})')
        match = bp_pattern.search(bp_text)

        if match:
            try:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))

                # Basic validation
                if 60 <= systolic <= 250 and 40 <= diastolic <= 150:
                    return systolic, diastolic
            except ValueError:
                pass

        return None, None

    @staticmethod
    def categorize_blood_pressure(systolic, diastolic):
        """
        Categorize blood pressure reading according to clinical guidelines.

        Args:
            systolic (int): Systolic blood pressure
            diastolic (int): Diastolic blood pressure

        Returns:
            str: Category ("Normal", "Elevated", "Hypertension Stage 1",
                          "Hypertension Stage 2", "Hypertensive Crisis")
        """
        if systolic is None or diastolic is None:
            return "Unknown"

        if systolic < 120 and diastolic < 80:
            return "Normal"
        elif 120 <= systolic <= 129 and diastolic < 80:
            return "Elevated"
        elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
            return "Hypertension Stage 1"
        elif systolic >= 140 or diastolic >= 90:
            return "Hypertension Stage 2"
        elif systolic > 180 or diastolic > 120:
            return "Hypertensive Crisis"
        else:
            return "Unknown"

    @staticmethod
    def format_date(date_obj=None, format_str="%Y-%m-%d"):
        """
        Format a date object as a string.

        Args:
            date_obj (datetime, optional): Date to format. Defaults to current date.
            format_str (str, optional): Format string. Defaults to "%Y-%m-%d".

        Returns:
            str: Formatted date string
        """
        if date_obj is None:
            date_obj = datetime.now()

        return date_obj.strftime(format_str)

    @staticmethod
    def ensure_directory_exists(directory_path):
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            directory_path (str): Path to the directory

        Returns:
            Path: Path object for the directory
        """
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def save_json(data, file_path):
        """
        Save data as a JSON file.

        Args:
            data (dict): Data to save
            file_path (str): Path to save the file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False

    @staticmethod
    def load_json(file_path):
        """
        Load data from a JSON file.

        Args:
            file_path (str): Path to the JSON file

        Returns:
            dict: Loaded data or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    @staticmethod
    def extract_symptoms_from_text(text):
        """
        Extract potential symptoms from text using keyword matching.

        Args:
            text (str): Text to analyze

        Returns:
            list: List of potential symptoms found
        """
        text = text.lower()

        # Common pregnancy-related symptoms to look for
        symptoms = [
            "headache", "blurry vision", "swelling", "edema",
            "nausea", "vomiting", "abdominal pain", "contractions",
            "bleeding", "spotting", "discharge", "fluid",
            "fever", "chills", "dizziness", "fatigue",
            "shortness of breath", "difficulty breathing",
            "reduced movement", "decreased movement", "no movement",
            "itching", "rash", "pain", "cramps", "back pain"
        ]

        found_symptoms = []
        for symptom in symptoms:
            if symptom in text:
                # Check for modifiers like "severe", "mild", "no", etc.
                for modifier in ["severe", "extreme", "intense", "bad", "worst"]:
                    if f"{modifier} {symptom}" in text:
                        found_symptoms.append(f"severe {symptom}")
                        break
                else:
                    for modifier in ["mild", "slight", "minor", "little"]:
                        if f"{modifier} {symptom}" in text:
                            found_symptoms.append(f"mild {symptom}")
                            break
                    else:
                        for modifier in ["no", "not", "don't have", "doesn't have", "without"]:
                            if re.search(rf"\b{modifier}\b.*\b{symptom}\b", text):
                                found_symptoms.append(f"no {symptom}")
                                break
                        else:
                            found_symptoms.append(symptom)

        return found_symptoms

    @staticmethod
    def get_env_variable(name, default=None):
        """
        Get an environment variable, with an optional default value.

        Args:
            name (str): Name of the environment variable
            default (any, optional): Default value if not found

        Returns:
            str: Value of the environment variable or default
        """
        return os.environ.get(name, default)

    @staticmethod
    def truncate_text(text, max_length=100, suffix="..."):
        """
        Truncate text to a maximum length.

        Args:
            text (str): Text to truncate
            max_length (int, optional): Maximum length. Defaults to 100.
            suffix (str, optional): Suffix to add if truncated. Defaults to "...".

        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
