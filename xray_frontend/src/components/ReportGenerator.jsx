import React, { useState } from 'react';

// Using the provided patient.json as a template for the initial state
const INITIAL_STATE = {
  patient_details: { name: "Anjali Sharma", age: 68, gender: "Female" },
  medical_history: {
    symptoms: "Persistent fatigue and weakness, Aching joints, Increased frequency of urination, Occasional blurry vision",
    existing_conditions: "Osteoporosis, Mild hypertension",
    allergies: "Sulfa drugs",
    family_history: "Mother had Type 2 Diabetes, Father had hypertension."
  },
  recent_lab_results: {
    blood_pressure: "135/85 mmHg",
    fasting_blood_sugar: "140 mg/dL",
    hba1c: "7.2%",
    vitamin_d_level: "18 ng/mL",
    esr_erythrocyte_sedimentation_rate: "25 mm/hr"
  }
};

const ReportGenerator = () => {
  const [formData, setFormData] = useState(INITIAL_STATE);
  const [report, setReport] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleGenerateReport = async () => {
    setIsLoading(true);
    setError('');
    setReport('');

    // Convert comma-separated strings to arrays for the final JSON
    const finalData = {
        ...formData,
        medical_history: {
            ...formData.medical_history,
            symptoms: formData.medical_history.symptoms.split(',').map(s => s.trim()),
            existing_conditions: formData.medical_history.existing_conditions.split(',').map(s => s.trim()),
            allergies: formData.medical_history.allergies.split(',').map(s => s.trim()),
        }
    };
    
    try {
      const response = await fetch('http://127.0.0.1:5000/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(finalData)
      });
      if (!response.ok) throw new Error('Server returned an error');
      const data = await response.json();
      setReport(data.report_text);
    } catch (err) {
      setError(`Failed to generate report: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="report-generator" className="report-generator-section">
      <h2>AI Medical Report Generator</h2>
      <div className="report-layout">
        <div className="report-form card">
          <h3 className="card-title">Enter Patient Data</h3>
          
          <h4>Patient Details</h4>
          <input type="text" value={formData.patient_details.name} onChange={e => handleInputChange('patient_details', 'name', e.target.value)} placeholder="Name" />
          <input type="number" value={formData.patient_details.age} onChange={e => handleInputChange('patient_details', 'age', e.target.value)} placeholder="Age" />

          <h4>Medical History</h4>
          <textarea rows="3" value={formData.medical_history.symptoms} onChange={e => handleInputChange('medical_history', 'symptoms', e.target.value)} placeholder="Symptoms (comma-separated)"></textarea>
          <textarea rows="2" value={formData.medical_history.existing_conditions} onChange={e => handleInputChange('medical_history', 'existing_conditions', e.target.value)} placeholder="Existing Conditions (comma-separated)"></textarea>
          
          <h4>Recent Lab Results</h4>
          <input type="text" value={formData.recent_lab_results.fasting_blood_sugar} onChange={e => handleInputChange('recent_lab_results', 'fasting_blood_sugar', e.target.value)} placeholder="Fasting Blood Sugar" />
          <input type="text" value={formData.recent_lab_results.hba1c} onChange={e => handleInputChange('recent_lab_results', 'hba1c', e.target.value)} placeholder="HbA1c" />

          <button onClick={handleGenerateReport} className="cta-button" disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
        <div className="report-display card">
            <h3 className="card-title">Generated Report</h3>
            {isLoading && <p>AI is generating the report, please wait...</p>}
            {error && <p style={{color: 'red'}}>{error}</p>}
            {report && <pre className="report-text">{report}</pre>}
        </div>
      </div>
    </section>
  );
};

export default ReportGenerator;