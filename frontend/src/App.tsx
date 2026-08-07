import { HashRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, motion, Variants } from "framer-motion";
import { Dashboard } from "./components/Dashboard";
import { Users } from "./components/Users";
import { Audiences } from "./components/Audiences";
import { Journeys } from "./components/Journeys";
import { Decisions } from "./components/Decisions";
import { Consents } from "./components/Consents";
import { Events } from "./components/Events";
import { Experiments } from "./components/Experiments";
import { Navigation } from "./components/Navigation";

const pageVariants: Variants = {
  initial: { opacity: 0, y: 15, scale: 0.99 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: "easeOut" } },
  exit: { opacity: 0, y: -15, scale: 0.99, transition: { duration: 0.3, ease: "easeIn" } }
};

const PageWrapper = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    initial="initial"
    animate="animate"
    exit="exit"
    variants={pageVariants}
    style={{ width: '100%', display: 'flex', flexDirection: 'column', flexGrow: 1 }}
  >
    {children}
  </motion.div>
);

const AnimatedRoutes = () => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageWrapper><Dashboard /></PageWrapper>} />
        <Route path="/users" element={<PageWrapper><Users /></PageWrapper>} />
        <Route path="/audiences" element={<PageWrapper><Audiences /></PageWrapper>} />
        <Route path="/journeys" element={<PageWrapper><Journeys /></PageWrapper>} />
        <Route path="/decisions" element={<PageWrapper><Decisions /></PageWrapper>} />
        <Route path="/consents" element={<PageWrapper><Consents /></PageWrapper>} />
        <Route path="/events" element={<PageWrapper><Events /></PageWrapper>} />
        <Route path="/experiments" element={<PageWrapper><Experiments /></PageWrapper>} />
      </Routes>
    </AnimatePresence>
  );
};

function App() {
  return (
    <Router>
      <div className="App" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%' }}>
        <Navigation />
        <AnimatedRoutes />
      </div>
    </Router>
  );
}

export default App;
