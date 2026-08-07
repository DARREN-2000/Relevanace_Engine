import { useEffect, useState } from 'react';
import axios from 'axios';

export const Users = () => {
    const [users, setUsers] = useState<any[]>([]);

    useEffect(() => {
        axios.get('http://localhost:8000/api/users')
            .then(res => setUsers(res.data.users))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setUsers([
                    { id: '1', email: 'jane@example.com', lifecycle_stage: 'trial', fatigue_score: 0.1, intent_score: 0.9 },
                    { id: '2', email: 'john@example.com', lifecycle_stage: 'active', fatigue_score: 0.8, intent_score: 0.2 },
                    { id: '3', email: 'alice@example.com', lifecycle_stage: 'churn_risk', fatigue_score: 0.5, intent_score: 0.4 },
                ]);
            });
    }, []);

    return (
        <div className="page-container">
            <h1>Users</h1>
            <table>
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Lifecycle Stage</th>
                        <th>Fatigue Score</th>
                        <th>Intent Score</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map(u => (
                        <tr key={u.id}>
                            <td>{u.email}</td>
                            <td>{u.lifecycle_stage}</td>
                            <td>{u.fatigue_score}</td>
                            <td>{u.intent_score}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
