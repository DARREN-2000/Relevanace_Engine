import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, UserPlus, Send, CheckCircle2, ShieldCheck, Activity, TestTube } from 'lucide-react';

export const Navigation = () => {
    const location = useLocation();

    const navStyle: React.CSSProperties = {
        padding: '15px 30px',
        background: 'rgba(5, 5, 5, 0.4)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        gap: '25px',
        alignItems: 'center',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        overflowX: 'auto',
    };

    const linkStyle = (path: string): React.CSSProperties => ({
        color: location.pathname === path ? '#fff' : '#a1a1aa',
        textDecoration: 'none',
        fontWeight: location.pathname === path ? 600 : 500,
        fontSize: '0.95rem',
        padding: '10px 0',
        borderBottom: location.pathname === path ? '2px solid #6366f1' : '2px solid transparent',
        transition: 'all 0.3s ease',
        whiteSpace: 'nowrap',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
    });

    const brandStyle: React.CSSProperties = {
        fontFamily: "'Outfit', sans-serif",
        fontWeight: 800,
        fontSize: '1.2rem',
        background: 'linear-gradient(to right, #6366f1, #ec4899)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        marginRight: '20px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
    };

    return (
        <nav style={navStyle}>
            <div style={brandStyle}>
                <ShieldCheck size={24} color="#6366f1" /> Dashboard
            </div>
            <Link to="/" style={linkStyle('/')}><LayoutDashboard size={18} /> Overview</Link>
            <Link to="/users" style={linkStyle('/users')}><Users size={18} /> Users</Link>
            <Link to="/audiences" style={linkStyle('/audiences')}><UserPlus size={18} /> Audiences</Link>
            <Link to="/journeys" style={linkStyle('/journeys')}><Send size={18} /> Journeys</Link>
            <Link to="/decisions" style={linkStyle('/decisions')}><CheckCircle2 size={18} /> Decisions</Link>
            <Link to="/consents" style={linkStyle('/consents')}><ShieldCheck size={18} /> Consents</Link>
            <Link to="/events" style={linkStyle('/events')}><Activity size={18} /> Events</Link>
            <Link to="/experiments" style={linkStyle('/experiments')}><TestTube size={18} /> Experiments</Link>
        </nav>
    );
};
