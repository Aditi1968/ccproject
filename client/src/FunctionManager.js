import React, { useEffect, useState } from 'react';
import axios from 'axios';

function FunctionManager() {
  const [functions, setFunctions] = useState([]);
  const [newFunc, setNewFunc] = useState({ name: '', route: '', language: 'python', timeout: 5, filename: ''});
  const [editId, setEditId] = useState(null);
  const [editFunc, setEditFunc] = useState({});

  useEffect(() => {
    loadFunctions();
  }, []);

  const loadFunctions = () => {
    axios.get('http://127.0.0.1:8000/functions/')
      .then(res => setFunctions(res.data))
      .catch(err => console.error('Error loading functions:', err.message));
  };

  const handleCreate = () => {
    axios.post('http://127.0.0.1:8000/functions/', newFunc)
      .then(() => {
        setNewFunc({ name: '', route: '', language: 'python', timeout: 5 });
        loadFunctions();
      })
      .catch(err => console.error('Error creating function:', err.message));
  };

  const handleDelete = (id) => {
    axios.delete(`http://127.0.0.1:8000/functions/${id}`)
      .then(() => loadFunctions())
      .catch(err => console.error('Error deleting function:', err.message));
  };

  const handleEdit = (func) => {
    setEditId(func.id);
    setEditFunc({ ...func });
  };

  const handleEditSave = () => {
    axios.put(`http://127.0.0.1:8000/functions/${editId}`, editFunc)
      .then(() => {
        setEditId(null);
        setEditFunc({});
        loadFunctions();
      })
      .catch(err => console.error('Error updating function:', err.message));
  };

  const handleRun = (id) => {
    axios.post(`http://127.0.0.1:8000/functions/${id}/run`)
      .then(res => alert(`✅ Output:\n${res.data.output}`))
      .catch(err => {
        const msg = err?.response?.data?.detail || err.message;
        alert(`❌ Error running function: ${msg}`);
      });
  };

  return (
    <div>
      <h2>🚀 Function Manager</h2>

      <div style={{ marginBottom: 20 }}>
        <input placeholder="Name" value={newFunc.name} onChange={e => setNewFunc({ ...newFunc, name: e.target.value })} />
        <input placeholder="Route" value={newFunc.route} onChange={e => setNewFunc({ ...newFunc, route: e.target.value })} />
        <input placeholder="Language" value={newFunc.language} onChange={e => setNewFunc({ ...newFunc, language: e.target.value })} />
        <input type="number" placeholder="Timeout" value={newFunc.timeout} onChange={e => setNewFunc({ ...newFunc, timeout:      Number(e.target.value) })} />
        <input placeholder="Filename" value={newFunc.filename || ''} onChange={e => setNewFunc({ ...newFunc, filename: e.target.value })} />
        <button onClick={handleCreate}>Add Function</button>

      </div>

      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Route</th>
            <th>Language</th>
            <th>Timeout</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {functions.map(fn => (
            <tr key={fn.id}>
              {editId === fn.id ? (
                <>
                  <td>{fn.id}</td>
                  <td><input value={editFunc.name} onChange={e => setEditFunc({ ...editFunc, name: e.target.value })} /></td>
                  <td><input value={editFunc.route} onChange={e => setEditFunc({ ...editFunc, route: e.target.value })} /></td>
                  <td><input value={editFunc.language} onChange={e => setEditFunc({ ...editFunc, language: e.target.value })} /></td>
                  <td><input type="number" value={editFunc.timeout} onChange={e => setEditFunc({ ...editFunc, timeout: Number(e.target.value) })} /></td>
                  <td>
                    <button onClick={handleEditSave}>Save</button>
                    <button onClick={() => setEditId(null)}>Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  <td>{fn.id}</td>
                  <td>{fn.name}</td>
                  <td>{fn.route}</td>
                  <td>{fn.language}</td>
                  <td>{fn.timeout}</td>
                  <td>
                    <button onClick={() => handleEdit(fn)}>Edit</button>
                    <button onClick={() => handleDelete(fn.id)}>Delete</button>
                    <button onClick={() => handleRun(fn.id)}>Run</button>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default FunctionManager;
