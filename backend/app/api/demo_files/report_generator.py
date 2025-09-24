import google.generativeai as genai
import json
from fpdf import FPDF
import os

# --- Configuration ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual Google AI API key.
# You can get your key from https://aistudio.google.com/app/apikey
API_KEY = "AIzaSyCiB83vyRj1DvVv0U4jWoIH8rUlO5kQ20A"

# Name for the input JSON file
PATIENT_DATA_FILE = "patient.json"

# Name for the output PDF file
OUTPUT_PDF_FILE = "patient_report.pdf"

# --- Main Functions ---

def create_patient_json_template():
    """Creates a template patient.json file if it doesn't exist."""
    if not os.path.exists(PATIENT_DATA_FILE):
        print(f"Creating a template '{PATIENT_DATA_FILE}' file.")
        patient_template = {
            "patient_details": {
                "name": "John Doe",
                "age": 45,
                "gender": "Male"
            },
            "medical_history": {
                "symptoms": ["chest pain", "shortness of breath", "dizziness"],
                "existing_conditions": ["hypertension", "type 2 diabetes"],
                "allergies": ["penicillin"],
                "family_history": "Father had a history of heart disease."
            },
            "recent_lab_results": {
                "cholesterol": "220 mg/dL",
                "blood_pressure": "140/90 mmHg",
                "blood_sugar": "150 mg/dL"
            }
        }
        with open(PATIENT_DATA_FILE, 'w') as f:
            json.dump(patient_template, f, indent=4)
        print("Please fill in the patient's details in the newly created 'patient.json' file and run the script again.")
        return False
    return True

def read_patient_data(filename):
    """Reads patient data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{filename}' contains invalid JSON. Please check the format.")
        return None

def generate_prompt(patient_data):
    """Generates the prompt for the Gemini API."""
    # Convert patient data to a string for the prompt
    patient_data_str = json.dumps(patient_data, indent=2)

    prompt = f"""
    Based on the following patient data:
    {patient_data_str}

    Please provide a structured report covering the following sections. Use clear headings for each section.
    1.  **Potential Illnesses or Conditions:** Analyze the symptoms, medical history, and lab results to suggest potential conditions.
    2. **Potential Causes** Recommend potential causes for the conditions
    3.  **Recommended Precautions:** Provide actionable lifestyle, dietary, and other precautions.
    4.  **Potential Risk Factors:** Highlight the key risk factors based on the provided data.
    5.  **Medication Suggestions:** Recommend potential medications that a doctor might consider.
    """
    return prompt

def get_gemini_response(api_key, prompt):
    """Sends the prompt to the Gemini API and gets the response."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        # Clean up the response text from markdown-like formatting for better PDF rendering
        cleaned_text = response.text.replace('**', '').replace('*', '')
        return cleaned_text
    except Exception as e:
        print(f"\nAn error occurred while contacting the Gemini API: {e}")
        print("Please check your API key and internet connection.")
        return None

def create_pdf_report(title, report_text, filename):
    """Creates a PDF file from the given text."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10) # Add a line break
    
    # Set Body Text
    pdf.set_font("Arial", size=12)
    # The multi_cell is used for text that can span multiple lines and wrap automatically
    # We use encode('latin-1', 'replace') to handle potential unicode characters that FPDF doesn't support by default
    pdf.multi_cell(0, 10, txt=report_text.encode('latin-1', 'replace').decode('latin-1'))
    
    try:
        pdf.output(filename)
        print(f"\nSuccessfully generated PDF report: '{filename}'")
    except Exception as e:
        print(f"\nAn error occurred while creating the PDF: {e}")


def main():
    """Main function to run the script."""
    print("--- Patient Analysis Report Generator ---")

    # Check for API Key
    if API_KEY == "YOUR_API_KEY" or not API_KEY:
        print("\nERROR: Please replace 'YOUR_API_KEY' with your actual Google AI API key in the script.")
        return
        
    # Create and check for the patient data file
    if not create_patient_json_template():
        return

    # 1. Read patient data from JSON
    patient_data = read_patient_data(PATIENT_DATA_FILE)
    if not patient_data:
        return # Exit if file reading failed

    print("\nStep 1: Reading patient data... Done.")
    
    # 2. Generate the prompt
    prompt = generate_prompt(patient_data)
    print("Step 2: Generating prompt for Gemini API... Done.")

    # 3. Get response from Gemini API
    print("Step 3: Sending request to Gemini API... (This may take a moment)")
    report_content = get_gemini_response(API_KEY, prompt)
    
    if not report_content:
        print("Could not generate the report content. Exiting.")
        return
        
    print("Step 4: Received response from Gemini... Done.")
    
    # 4. Create the PDF report
    patient_name = patient_data.get("patient_details", {}).get("name", "Unknown Patient")
    report_title = f"Medical Analysis Report for {patient_name}"
    create_pdf_report(report_title, report_content, OUTPUT_PDF_FILE)

if __name__ == "__main__":
    main()
