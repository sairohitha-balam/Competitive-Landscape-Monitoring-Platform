import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Define the API endpoint
// Use the Vercel environment variable, or fall back to localhost for testing
// const API_URL = (process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000') + '/api/insights/';
const API_URL = 'https://monitor-backend.onrender.com/api/insights/';

// Define colors for our pie chart
const COLORS = {
  'RELEASE': '#43a047',
  'CAMPAIGN': '#1e88e5',
  'PRICING': '#f4511e',
  'HIRING': '#fb8c00',
  'NEWS': '#8e24aa',
  'UNKNOWN': '#78909c',
};

// A single "Insight" card component
const InsightCard = ({ insight }) => {
  // Format the date to be more readable
  const formattedDate = new Date(insight.event_date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="insight-card">
      <h3>{insight.title}</h3>
      <div className="meta">
        <span><strong>Competitor:</strong> {insight.competitor_name}</span>
        <span><strong>Found:</strong> {formattedDate}</span>
      </div>
      
      <span className={`category-badge category-${insight.category}`}>
        {insight.category_display}
      </span>

      <p>{insight.summary}</p>
      
      <a 
        href={insight.source_url} 
        target="_blank" 
        rel="noopener noreferrer" 
        className="source-link"
      >
        View Source
      </a>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // This function will run once when the component loads
    const fetchInsights = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get(API_URL);
        
        // 1. Set the main insights list
        setInsights(response.data);
        
        // 2. Process data for the pie chart
        const categoryCounts = response.data.reduce((acc, insight) => {
          const category = insight.category_display;
          acc[category] = (acc[category] || 0) + 1;
          return acc;
        }, {});
        
        const formattedChartData = Object.keys(categoryCounts).map(name => ({
          name,
          value: categoryCounts[name],
          color: COLORS[name.toUpperCase()] || '#78909c'
        }));
        
        setChartData(formattedChartData);
        
      } catch (err) {
        // We will *definitely* see an error here at first
        console.error("Fetch error:", err);
        setError("Failed to fetch data. (Check console for CORS error)");
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []); // The empty array [] means this effect runs only once

  if (loading) {
    return <div>Loading insights...</div>;
  }

  // We will show the error, but still render the rest of the page
  // so we can see the layout.
  const errorMessage = error ? <div className="error-message">{error}</div> : null;

  return (
    <div className="dashboard-container">
      <section className="insights-feed">
        <h2>Latest Insights</h2>
        {errorMessage}
        {insights.length > 0 ? (
          insights.map(insight => (
            <InsightCard key={insight.id} insight={insight} />
          ))
        ) : (
          !error && <p>No insights found.</p>
        )}
      </section>

      <aside className="insights-sidebar">
        <h2>Insights by Category</h2>
        <div className="chart-container">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
             <p>No data for chart.</p>
          )}
        </div>
      </aside>
    </div>
  );
};

export default Dashboard;