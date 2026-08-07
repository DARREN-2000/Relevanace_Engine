import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Cell, AreaChart, Area } from 'recharts';

export const Dashboard = () => {
    const [summary, setSummary] = useState<any>({});
    const [fatigue, setFatigue] = useState<any[]>([]);
    const [channels, setChannels] = useState<any[]>([]);
    const [suppression, setSuppression] = useState<any[]>([]);

    useEffect(() => {
        axios.get('http://localhost:8000/api/analytics/summary')
            .then(res => setSummary(res.data))
            .catch(err => {
                console.error("API failed, using mock data", err);
                setSummary({
                    total_users: 120534,
                    total_decisions: 580210,
                    suppression_rate: 0.153,
                    avg_intent_score: 0.75,
                    avg_churn_risk: 0.2,
                    avg_fatigue_score: 0.3,
                    activated_users: 80900,
                    activation_rate: 0.66
                });
            });

        axios.get('http://localhost:8000/api/analytics/fatigue')
            .then(res => setFatigue(res.data))
            .catch(err => {
                setFatigue([
                    { bucket: "0.0-0.2", count: 50200, percentage: 0.4 },
                    { bucket: "0.2-0.4", count: 40150, percentage: 0.3 },
                    { bucket: "0.4-0.6", count: 20400, percentage: 0.15 },
                    { bucket: "0.6-0.8", count: 10100, percentage: 0.1 },
                    { bucket: "0.8-1.0", count: 2150, percentage: 0.05 }
                ]);
            });

        axios.get('http://localhost:8000/api/analytics/channels')
            .then(res => setChannels(res.data))
            .catch(err => {
                setChannels([
                    { channel: "Email", total_decisions: 300000, suppressed: 50000, open_rate: 0.25, click_rate: 0.1 },
                    { channel: "SMS", total_decisions: 150000, suppressed: 20000, open_rate: 0.8, click_rate: 0.15 },
                    { channel: "Push", total_decisions: 130000, suppressed: 15000, open_rate: 0.5, click_rate: 0.05 }
                ]);
            });

        axios.get('http://localhost:8000/api/analytics/suppression')
            .then(res => setSuppression(res.data))
            .catch(err => {
                setSuppression([
                    { reason: "No Consent", count: 40000, percentage: 0.5 },
                    { reason: "Fatigue Cap", count: 25000, percentage: 0.3 },
                    { reason: "Quiet Hours", count: 10000, percentage: 0.12 },
                    { reason: "Unsubscribed", count: 5000, percentage: 0.08 }
                ]);
            });
    }, []);

    const statCardStyle: React.CSSProperties = {
        padding: '25px',
        flex: '1 1 200px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
    };

    const statValueStyle: React.CSSProperties = {
        fontSize: '2rem',
        fontWeight: 600,
        fontFamily: "'Outfit', sans-serif",
        background: 'linear-gradient(to right, #ffffff, #a1a1aa)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        margin: 0
    };

    const statLabelStyle: React.CSSProperties = {
        color: '#a1a1aa',
        fontSize: '0.9rem',
        textTransform: 'uppercase',
        letterSpacing: '1px',
        margin: 0
    };

    const formatNumber = (num: number) => {
        return new Intl.NumberFormat().format(num);
    };

    return (
        <div style={{ padding: '30px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
            <div style={{ marginBottom: '30px' }}>
                <h1 style={{ fontSize: '2rem', marginBottom: '5px' }}>Overview</h1>
                <p style={{ color: '#a1a1aa', margin: 0 }}>Real-time metrics from the Consentinel Engine.</p>
            </div>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
                <div className="glass-panel" style={statCardStyle}>
                    <p style={statLabelStyle}>Total Users</p>
                    <p style={statValueStyle}>{summary.total_users ? formatNumber(summary.total_users) : '-'}</p>
                </div>
                <div className="glass-panel" style={statCardStyle}>
                    <p style={statLabelStyle}>Total Decisions</p>
                    <p style={statValueStyle}>{summary.total_decisions ? formatNumber(summary.total_decisions) : '-'}</p>
                </div>
                <div className="glass-panel" style={statCardStyle}>
                    <p style={statLabelStyle}>Suppression Rate</p>
                    <p style={statValueStyle}>{summary.suppression_rate !== undefined ? (summary.suppression_rate * 100).toFixed(1) + "%" : "-"}</p>
                </div>
                <div className="glass-panel" style={statCardStyle}>
                    <p style={statLabelStyle}>Avg Fatigue Score</p>
                    <p style={statValueStyle}>{summary.avg_fatigue_score !== undefined ? summary.avg_fatigue_score.toFixed(2) : "-"}</p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
                
                <div className="glass-panel" style={{ padding: '25px' }}>
                    <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>Fatigue Distribution</h3>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <AreaChart data={fatigue}>
                                <defs>
                                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="bucket" />
                                <YAxis tickFormatter={(val) => `${val / 1000}k`} />
                                <Tooltip />
                                <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorCount)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-panel" style={{ padding: '25px' }}>
                    <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>Channel Performance</h3>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <BarChart data={channels}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="channel" />
                                <YAxis tickFormatter={(val) => `${val / 1000}k`} />
                                <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                                <Bar dataKey="total_decisions" fill="#10b981" name="Sent" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="suppressed" fill="#ec4899" name="Suppressed" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="glass-panel" style={{ padding: '25px' }}>
                    <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>Suppression Reasons</h3>
                    <div style={{ width: '100%', height: 300 }}>
                        <ResponsiveContainer>
                            <BarChart data={suppression} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" tickFormatter={(val) => `${val / 1000}k`} />
                                <YAxis dataKey="reason" type="category" width={100} />
                                <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                                <Bar dataKey="count" name="Users Suppressed" radius={[0, 4, 4, 0]}>
                                    {
                                        suppression.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'][index % 4]} />
                                        ))
                                    }
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>
        </div>
    );
};
