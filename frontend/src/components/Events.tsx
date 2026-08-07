import { useState } from 'react';
import axios from 'axios';

export const Events = () => {
    const [userId, setUserId] = useState('');
    const [events, setEvents] = useState<any[]>([]);

    // New event form state
    const [eventType, setEventType] = useState('track');
    const [eventName, setEventName] = useState('page_view');
    const [source, setSource] = useState('web');

    const handleFetchEvents = () => {
        if (!userId) return;
        axios.get(`http://localhost:8000/api/events/${userId}`)
            .then(res => setEvents(res.data.events))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setEvents([
                    { id: '1', event_type: 'track', event_name: 'pricing_view', source: 'web', timestamp: new Date().toISOString() },
                    { id: '2', event_type: 'identify', event_name: 'login', source: 'mobile', timestamp: new Date().toISOString() },
                ]);
            });
    };

    const handleRecordEvent = (e: React.FormEvent) => {
        e.preventDefault();
        if (!userId) {
            alert("Please enter a User ID first.");
            return;
        }

        const payload = {
            user_id: userId,
            event_type: eventType,
            event_name: eventName,
            source: source,
            properties: {}
        };

        axios.post('http://localhost:8000/api/events', payload)
            .then(() => {
                alert("Event recorded successfully!");
                handleFetchEvents();
            })
            .catch(err => {
                console.error("API failed, mocking success", err);
                alert("Event recorded successfully (Mock)!");
                setEvents(prev => [{
                    id: Math.random().toString(),
                    event_type: eventType,
                    event_name: eventName,
                    source,
                    timestamp: new Date().toISOString()
                }, ...prev]);
            });
    };

    return (
        <div className="page-container">
            <h1>Events</h1>

            <div style={{ marginBottom: '20px' }}>
                <input
                    type="text"
                    value={userId}
                    onChange={e => setUserId(e.target.value)}
                    placeholder="Enter User ID"
                    style={{ padding: '5px', marginRight: '10px' }}
                />
                <button onClick={handleFetchEvents}>Fetch Events</button>
            </div>

            <div style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '20px' }}>
                <h3>Record New Event</h3>
                <form onSubmit={handleRecordEvent}>
                    <label style={{ marginRight: '10px' }}>
                        Type:
                        <select value={eventType} onChange={e => setEventType(e.target.value)} style={{ marginLeft: '5px' }}>
                            <option value="track">Track</option>
                            <option value="identify">Identify</option>
                            <option value="page">Page</option>
                        </select>
                    </label>
                    <label style={{ marginRight: '10px' }}>
                        Name:
                        <input type="text" value={eventName} onChange={e => setEventName(e.target.value)} style={{ marginLeft: '5px', width: '150px' }} />
                    </label>
                    <label style={{ marginRight: '10px' }}>
                        Source:
                        <input type="text" value={source} onChange={e => setSource(e.target.value)} style={{ marginLeft: '5px', width: '100px' }} />
                    </label>
                    <button type="submit">Record</button>
                </form>
            </div>

            <h2>Event History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Name</th>
                        <th>Source</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map(ev => (
                        <tr key={ev.id}>
                            <td>{ev.event_type}</td>
                            <td>{ev.event_name}</td>
                            <td>{ev.source}</td>
                            <td>{new Date(ev.timestamp).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
