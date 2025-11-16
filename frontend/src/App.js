import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="App">
      <header className="header">
        <h1>📈 Competitive Landscape Monitor</h1>
        <p>Your real-time automated competitor insights platform</p>
      </header>
      
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;