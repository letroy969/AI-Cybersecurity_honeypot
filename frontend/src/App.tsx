import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Attacks from './pages/Attacks';
import Attackers from './pages/Attackers';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import Honeypots from './pages/Honeypots';
import Settings from './pages/Settings';

// Security-themed dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ef4444', // Alert red
      light: '#f87171',
      dark: '#dc2626',
    },
    secondary: {
      main: '#f59e0b', // Amber highlights
      light: '#fbbf24',
      dark: '#d97706',
    },
    background: {
      default: '#0f1724', // Charcoal
      paper: '#1e293b',   // Darker charcoal
    },
    text: {
      primary: '#ffffff',
      secondary: '#94a3b8',
    },
    error: {
      main: '#ef4444',
    },
    warning: {
      main: '#f59e0b',
    },
    info: {
      main: '#3b82f6',
    },
    success: {
      main: '#10b981',
    },
    divider: '#374151',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h4: {
      fontWeight: 500,
      fontSize: '1.25rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.125rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.75rem',
      lineHeight: 1.4,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid #374151',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
  },
});

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/attacks" element={<Attacks />} />
                <Route path="/attackers" element={<Attackers />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/honeypots" element={<Honeypots />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          </Box>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
