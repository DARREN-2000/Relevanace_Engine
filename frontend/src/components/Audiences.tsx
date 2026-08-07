import { useEffect, useState } from 'react';
import axios from 'axios';

export const Audiences = () => {
    const [audiences, setAudiences] = useState<any[]>([]);

    useEffect(() => {
        axios.get('http://localhost:8000/api/audiences')
            .then(res => setAudiences(res.data))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setAudiences([
                    { id: '1', name: 'High Intent Users', description: 'Users with high intent score and low fatigue', estimated_size: 1500 },
                    { id: '2', name: 'Churn Risk', description: 'Users showing signs of churning', estimated_size: 300 },
                    { id: '3', name: 'Recent Signups', description: 'Users who signed up in the last 7 days', estimated_size: 850 },
                ]);
            });
    }, []);

    return (
        <div className="page-container">
            <h1>Audience Segments</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Estimated Size</th>
                    </tr>
                </thead>
                <tbody>
                    {audiences.map(a => (
                        <tr key={a.id}>
                            <td>{a.name}</td>
                            <td>{a.description}</td>
                            <td>{a.estimated_size}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
