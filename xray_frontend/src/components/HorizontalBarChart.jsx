import React, { useState, useEffect } from 'react';

const HorizontalBarChart = ({ data }) => {
    const [isVisible, setIsVisible] = useState(false);
    useEffect(() => {
        const timer = setTimeout(() => setIsVisible(true), 100);
        return () => clearTimeout(timer);
    }, [data]);
    
    return (
        <div className={`h-chart-container ${isVisible ? 'visible' : ''}`}>
            {data.map((item, index) => 
                <div key={item.name} className="h-chart-row">
                    <div className="h-chart-label">{item.name}</div>
                    <div className="h-chart-bar-bg">
                        <div
                            className="h-chart-bar-fill"
                            style={{ 
                                width: `${item.confidence}%`,
                                transitionDelay: `${index * 0.05}s`
                            }}
                            title={`${item.name}: ${item.confidence}%`}
                        >
                           <span className="h-chart-value">{`${item.confidence}%`}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
export default HorizontalBarChart;