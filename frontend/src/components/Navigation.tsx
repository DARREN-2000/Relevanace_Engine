import { Link, useLocation } from 'react-router-dom';

export const Navigation = () => {
    const location = useLocation();

    const navStyle: React.CSSProperties = {
        padding: '15px 30px',
        background: 'rgba(255, 255, 255, 0.03)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(10px)',
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
        padding: '5px 0',
        borderBottom: location.pathname === path ? '2px solid #6366f1' : '2px solid transparent',
        transition: 'all 0.3s ease',
        whiteSpace: 'nowrap',
    });

    const brandStyle: React.CSSProperties = {
        fontFamily: "'Outfit', sans-serif",
        fontWeight: 800,
        fontSize: '1.2rem',
        background: 'linear-gradient(to right, #6366f1, #ec4899)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        marginRight: '20px',
    };

    return (
        <nav style={navStyle}>
            <div style={brandStyle}>Dashboard</div>
            <Link to="/" style={linkStyle('/')}>Overview</Link>
            <Link to="/users" style={linkStyle('/users')}>Users</Link>
            <Link to="/audiences" style={linkStyle('/audiences')}>Audiences</Link>
            <Link to="/journeys" style={linkStyle('/journeys')}>Journeys</Link>
            <Link to="/decisions" style={linkStyle('/decisions')}>Decisions</Link>
            <Link to="/consents" style={linkStyle('/consents')}>Consents</Link>
            <Link to="/events" style={linkStyle('/events')}>Events</Link>
            <Link to="/experiments" style={linkStyle('/experiments')}>Experiments</Link>
        </nav>
    );
};
