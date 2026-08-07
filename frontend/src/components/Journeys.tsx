import { useEffect, useState } from 'react';
import axios from 'axios';

export const Journeys = () => {
    const [templates, setTemplates] = useState<any[]>([]);

    useEffect(() => {
        axios.get('http://localhost:8000/api/journeys/templates')
            .then(res => setTemplates(res.data))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setTemplates([
                    { id: '1', name: 'Onboarding Sequence', goal: 'Activate user', is_active: true },
                    { id: '2', name: 'Churn Prevention', goal: 'Retain user', is_active: true },
                    { id: '3', name: 'Upsell Campaign', goal: 'Upgrade to Pro', is_active: false },
                ]);
            });
    }, []);

    return (
        <div className="page-container">
            <h1>Journey Templates</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Goal</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {templates.map(t => (
                        <tr key={t.id}>
                            <td>{t.name}</td>
                            <td>{t.goal}</td>
                            <td>{t.is_active ? "Active" : "Inactive"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
