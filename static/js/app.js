const e = React.createElement;

// --- Navbar Component (Updated Logo) ---
const Navbar = () => {
    const [scrolled, setScrolled] = React.useState(false);
    React.useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);
    return e('nav', { className: `navbar ${scrolled ? 'scrolled' : ''}` },
        // 1. Logo text changed
        e('a', { href: '#hero', className: 'logo' }, 'CXR-Vision', e('span', null, 'AI')),
        e('ul', { className: 'nav-links' },
            e('li', null, e('a', { href: '#upload' }, 'Analyzer')),
            e('li', null, e('a', { href: '#footer' }, 'About'))
        )
    );
};

// --- Hero Component ---
const Hero = () => {
    const title = "AI-Powered-X-Ray-Analysis";
    return e('section', { id: 'hero', className: 'hero' },
        e('h1', { className: 'hero-title' },
            title.split("").map((letter, index) =>
                e('span', { key: index, className: 'letter', style: { animationDelay: `${index * 0.05}s` } }, letter === " " ? "\\u00A0" : letter)
            )
        ),
        e('p', { className: 'hero-tagline' }, 'Instant, Accurate, and Transparent Thoracic Pathology Detection.'),
        e('a', { href: '#upload', className: 'cta-button pulse' }, 'Upload X-Ray')
    );
};

// --- New Horizontal BarChart Component ---
const HorizontalBarChart = ({ data }) => {
    const [isVisible, setIsVisible] = React.useState(false);
    React.useEffect(() => {
        const timer = setTimeout(() => setIsVisible(true), 100);
        return () => clearTimeout(timer);
    }, [data]);
    
    return e('div', { className: `h-chart-container ${isVisible ? 'visible' : ''}` },
        data.map((item, index) => 
            e('div', { key: item.name, className: 'h-chart-row' },
                e('div', { className: 'h-chart-label' }, item.name),
                e('div', { className: 'h-chart-bar-bg' },
                    e('div', {
                        className: 'h-chart-bar-fill',
                        style: { 
                            width: `${item.confidence}%`,
                            transitionDelay: `${index * 0.05}s`
                        },
                        title: `${item.name}: ${item.confidence}%`
                    },
                       e('span', { className: 'h-chart-value'}, `${item.confidence}%`)
                    )
                )
            )
        )
    );
};

// --- Upload Component (Using new Chart) ---
const Upload = () => {
    const [isAnalyzing, setIsAnalyzing] = React.useState(false);
    const [file, setFile] = React.useState(null);
    const [fileURL, setFileURL] = React.useState('');
    const [predictions, setPredictions] = React.useState([]);
    const [heatmaps, setHeatmaps] = React.useState([]);
    const [error, setError] = React.useState('');

    const onDrop = React.useCallback(acceptedFiles => {
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
            const response = await fetch('/analyze', { method: 'POST', body: formData });
            if (!response.ok) throw new Error(`Server error: ${response.statusText}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            setPredictions(data.predictions);
            setHeatmaps(data.heatmaps || []);
        } catch (err) {
            setError(`Analysis failed: ${err.message}`);
        } finally {
            setIsAnalyzing(false);
        }
    };
    
    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'image/*': ['.png', '.jpeg', '.jpg']} });

    const topFindings = predictions.filter(p => p.confidence > 50);

    return e('section', { id: 'upload' },
        e('h2', null, 'AI Prediction Analyzer'),
        e('div', { className: 'upload-panel' },
            e('div', { ...getRootProps(), className: `drop-zone ${isDragActive ? 'drag-over' : ''}` },
                e('input', { ...getInputProps() }),
                file ? e('p', null, `✅ File ready: ${file.name}`) : e('p', null, 'Drag & drop an X-ray image here, or click to select')
            ),
            e('button', { onClick: handleAnalyze, className: 'cta-button', disabled: isAnalyzing || !file },
                isAnalyzing ? 'Analyzing...' : 'Analyze Image'
            )
        ),
        error && e('p', { style: { color: 'red', textAlign: 'center', marginTop: '20px' } }, error),
        
        predictions.length > 0 && e('div', { className: 'analysis-dashboard' },
            e('div', { className: 'image-display-card' },
                e('h3', { style: { marginTop: 0 } }, 'Uploaded Image'),
                e('img', { src: fileURL, alt: 'Uploaded X-Ray' })
            ),
            e('div', { className: 'results-card' },
                e('h3', { style: { marginTop: 0 } }, 'Analysis Report'),
                topFindings.length > 0 ?
                    e('p', null, 'The model has identified the following potential findings:') :
                    e('p', null, 'No significant pathologies detected above the 50% confidence threshold.'),
                topFindings.map(finding => e('li', {key: finding.name}, `${finding.name}`)),
                e(HorizontalBarChart, { data: predictions }) // Using the new Horizontal Bar Chart
            )
        ),

        heatmaps.length > 0 && e('div', null,
            e('hr', {className: 'section-divider'}),
            e('h2', {style: {fontSize: '2rem'}}, 'Explainable AI (XAI) Visualizations'),
            e('p', { style: { textAlign: 'center', color: 'var(--text-secondary)', marginTop: '-40px', marginBottom: '40px' } }, 'The highlighted areas show where the AI focused to make its predictions.'),
            e('div', { className: 'heatmap-grid' },
                heatmaps.map((heatmap, index) =>
                    e('div', { className: 'heatmap-card', key: index, style: { animationDelay: `${index * 0.15}s` } },
                        e('img', { src: `data:image/png;base64,${heatmap.image}` }),
                        e('h4', null, heatmap.disease)
                    )
                )
            )
        )
    );
};

// --- Footer Component ---
const Footer = () => e('footer', { id: 'footer', className: 'footer' }, e('p', null, '© 2025 CXR-Vision AI. All Rights Reserved. For informational and educational purposes only.'));

// --- Main App Component ---
const App = () => e(React.Fragment, null, e(Navbar), e('main', null, e(Hero), e(Upload)), e(Footer));

// --- Render the App ---
const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
const useDropzone = ({ onDrop, accept }) => { // Simplified dropzone for transpiled env
    const onDragOver = e => e.preventDefault();
    const handleDrop = e => { e.preventDefault(); onDrop(Array.from(e.dataTransfer.files)); };
    const openFileDialog = () => {
        const input = document.createElement('input');
        input.type = 'file'; input.accept = Object.keys(accept).join(',');
        input.onchange = e => onDrop(Array.from(e.target.files));
        input.click();
    };
    const getRootProps = () => ({ onDragOver, onDrop, onClick: openFileDialog });
    const getInputProps = () => ({});
    return { getRootProps, getInputProps, isDragActive: false };
};
root.render(e(App));