import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import FunctionManager from './FunctionManager';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

function App() {
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/metrics')
      .then(res => setMetrics(res.data))
      .catch(err => console.error('Error loading metrics', err));
  }, []);

  const runtimes = metrics.reduce((acc, m) => {
    acc[m.runtime] = (acc[m.runtime] || 0) + 1;
    return acc;
  }, {});

  const successRate = metrics.reduce((acc, m) => {
    if (m.success) acc.success++;
    else acc.fail++;
    return acc;
  }, { success: 0, fail: 0 });

  const avgTime = metrics.length
    ? (metrics.reduce((acc, m) => acc + m.duration, 0) / metrics.length).toFixed(2)
    : 0;

  return (
    <div style={{ padding: 20 }}>
      <h1>📊 Function Execution Dashboard</h1>

      {/* Function CRUD UI */}
      <FunctionManager />

      <hr />

      <p><strong>Total Runs:</strong> {metrics.length}</p>
      <p><strong>Average Execution Time:</strong> {avgTime} seconds</p>

      <div style={{ display: 'flex', gap: 40 }}>
        <div style={{ width: 300 }}>
          <h3>Runtime Distribution</h3>
          <Bar
            data={{
              labels: Object.keys(runtimes),
              datasets: [{
                label: '# of Executions',
                data: Object.values(runtimes),
              }],
            }}
          />
        </div>

        <div style={{ width: 300 }}>
          <h3>Success vs Failure</h3>
          <Pie
            data={{
              labels: ['Success', 'Failure'],
              datasets: [{
                data: [successRate.success, successRate.fail],
                backgroundColor: ['#4caf50', '#f44336'],
              }],
            }}
          />
        </div>
      </div>

      <h3>Execution Log</h3>
      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Runtime</th>
            <th>Duration (s)</th>
            <th>Success</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((m, i) => (
            <tr key={i}>
              <td>{m.runtime}</td>
              <td>{m.duration}</td>
              <td>{m.success ? '✅' : '❌'}</td>
              <td>{new Date(m.timestamp * 1000).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
