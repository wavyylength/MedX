import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import HorizontalBarChart from './HorizontalBarChart';
// The import for saveAnalysis is no longer needed

const Upload = () => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [file, setFile] = useState(null);
    const [fileURL, setFileURL] = useState('');
    const [predictions, setPredictions] = useState([]);
    const [heatmaps, setHeatmaps] = useState([]);
    const [error, setError] = useState('');

    const onDrop = useCallback(acceptedFiles => {
        const currentFile = acceptedFiles[0];
        setFile(currentFile);
        setFileURL(URL.createObjectURL(currentFile));
        setPredictions([]);
        setHeatmaps([]);
        setError('');
    }, []);
    
    const handleAnalyze = async () => {
        if (!file) return;
        setIsAnalyzing(true);
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('http://127.0.0.1:5000/analyze', { 
                method: 'POST', 
                body: formData 
            });

            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);

            setPredictions(data.predictions);
            setHeatmaps(data.heatmaps || []);

            // The logic to save to history has been removed from this section

        } catch (err) {
            setError(`Analysis failed: ${err.message}. Ensure the Python server is running.`);
        } finally {
            setIsAnalyzing(false);
        }
    };
    
    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'image/*': ['.png', '.jpeg', '.jpg']} });
    const topFindings = predictions.filter(p => p.confidence > 50);

    return (
        <section id="upload">
            <h2>AI Prediction Analyzer</h2>
            <div className="upload-panel">
                <div {...getRootProps()} className={`drop-zone ${isDragActive ? 'drag-over' : ''}`}>
                    <input {...getInputProps()} />
                    {file ? <p>✅ File ready: {file.name}</p> : <p>Drag & drop an X-ray image here, or click to select</p>}
                </div>
                <button onClick={handleAnalyze} className="cta-button" disabled={isAnalyzing || !file}>
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Image'}
                </button>
            </div>
            {error && <p style={{ color: 'red', textAlign: 'center', marginTop: '20px' }}>{error}</p>}
            
            {predictions.length > 0 && (
                <div className="analysis-dashboard">
                    <div className="image-display-card">
                        <h3 style={{ marginTop: 0 }}>Uploaded Image</h3>
                        <img src={fileURL} alt="Uploaded X-Ray" />
                    </div>
                    <div className="results-card">
                        <h3 style={{ marginTop: 0 }}>Analysis Report</h3>
                        <p>{topFindings.length > 0 ? 'The model has identified the following potential findings:' : 'No significant pathologies detected above the 50% confidence threshold.'}</p>
                        <ul>{topFindings.map(finding => <li key={finding.name}>{finding.name}</li>)}</ul>
                        <HorizontalBarChart data={predictions} />
                    </div>
                </div>
            )}
            {heatmaps.length > 0 && (
                <div>
                    <hr className="section-divider" />
                    <h2 style={{ fontSize: '2rem' }}>Explainable AI (XAI) Visualizations</h2>
                    <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '-40px', marginBottom: '40px' }}>The highlighted areas show where the AI focused to make its predictions.</p>
                    <div className="heatmap-grid">
                        {heatmaps.map((heatmap, index) =>
                            <div className="heatmap-card" key={index} style={{ animationDelay: `${index * 0.15}s` }}>
                                <img src={`data:image/png;base64,${heatmap.image}`} />
                                <h4>{heatmap.disease}</h4>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </section>
    );
};
export default Upload;