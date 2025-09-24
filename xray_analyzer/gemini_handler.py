import google.generativeai as genai
import os
import json
from dotenv import load_dotenv # ✨ 1. Import load_dotenv

load_dotenv() # ✨ 2. Load the variables from your .env file

# --- Configuration ---
# ✨ 3. Read the key securely from the environment
API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_prompt(patient_data):
    """Generates the prompt for the Gemini API from a dictionary."""
    patient_data_str = json.dumps(patient_data, indent=2)
    prompt = f"""
    Based on the following patient data:
    {patient_data_str}

    Please provide a structured medical analysis report covering the following sections. Use clear headings for each section.
    1. **Potential Illnesses or Conditions:** Analyze the symptoms, medical history, and lab results to suggest potential conditions.
    2. **Potential Causes:** Explain the likely causes for the identified conditions.
    3. **Recommended Precautions:** Provide actionable lifestyle, dietary, and other precautions.
    4. **Potential Risk Factors:** Highlight the key risk factors based on the provided data.
    5. **Medication Suggestions:** Recommend potential medications that a doctor MIGHT consider, prefacing with a strong recommendation to consult a physician.
    6. **Disclaimer:** Add a standard medical AI disclaimer at the end.
    """
    return prompt

def generate_report_from_gemini(patient_data):
    """
    Takes patient data, calls the Gemini API, and returns the generated report text.
    """
    if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("ERROR: Gemini API Key is not configured in gemini_handler.py")
        return "Error: The Gemini API key is not configured on the server."

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = generate_prompt(patient_data)
        print("Sending request to Gemini API for report generation...")
        response = model.generate_content(prompt)
        
        # Clean up the response text from markdown for better display
        cleaned_text = response.text.replace('**', '').replace('*', '')
        print("Successfully received and cleaned response from Gemini.")
        return cleaned_text
        
    except Exception as e:
        print(f"\nAn error occurred while contacting the Gemini API: {e}")
        return f"An error occurred while generating the report: {e}"    