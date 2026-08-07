import { useState } from 'react';
import axios from 'axios';

export const Decisions = () => {
    const [userId, setUserId] = useState('');
    const [history, setHistory] = useState<any[]>([]);
    const [nbaResult, setNbaResult] = useState<any>(null);

    const handleRunNba = () => {
        axios.post('http://localhost:8000/api/decisions/next-best-action', { user_id: userId })
            .then(res => setNbaResult(res.data))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setNbaResult({
                    id: 'mock-123',
                    channel: 'email',
                    action: 'send_newsletter',
                    reason: 'high intent score',
                    suppressed: false
                });
            });
    };

    const handleFetchHistory = () => {
        axios.get(`http://localhost:8000/api/decisions/${userId}`)
            .then(res => setHistory(res.data.decisions))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setHistory([
                    { id: '1', channel: 'email', action: 'send_newsletter', suppressed: false, created_at: new Date().toISOString() },
                    { id: '2', channel: 'none', action: 'none', suppressed: true, suppression_reason: 'fatigue', created_at: new Date().toISOString() },
                ]);
            });
    };

    return (
        <div className="page-container">
            <h1>Decisions (Next Best Action)</h1>
            <div style={{ marginBottom: '20px' }}>
                <input
                    type="text"
                    value={userId}
                    onChange={e => setUserId(e.target.value)}
                    placeholder="Enter User ID"
                    style={{ padding: '5px', marginRight: '10px' }}
                />
                <button onClick={handleRunNba} style={{ marginRight: '10px' }}>Run NBA</button>
                <button onClick={handleFetchHistory}>Fetch History</button>
            </div>

            {nbaResult && (
                <div style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '20px' }}>
                    <h3>Latest NBA Result</h3>
                    <p><strong>Channel:</strong> {nbaResult.channel}</p>
                    <p><strong>Action:</strong> {nbaResult.action}</p>
                    <p><strong>Reason:</strong> {nbaResult.reason}</p>
                    <p><strong>Suppressed:</strong> {nbaResult.suppressed ? "Yes" : "No"}</p>
                </div>
            )}

            <h2>Decision History</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Channel</th>
                        <th>Action</th>
                        <th>Suppressed</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {history.map(h => (
                        <tr key={h.id}>
                            <td>{h.id}</td>
                            <td>{h.channel}</td>
                            <td>{h.action}</td>
                            <td>{h.suppressed ? h.suppression_reason || "Yes" : "No"}</td>
                            <td>{new Date(h.created_at).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
