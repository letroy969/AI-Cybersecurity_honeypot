import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security as SecurityIcon,
  People as PeopleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';

// Components
import AttackTimeline from '../components/AttackTimeline';
import AttackMap from '../components/AttackMap';
import RecentAttacks from '../components/RecentAttacks';
import TopAttackers from '../components/TopAttackers';

// Mock data for demonstration
const mockAnalytics = {
  totalAttacks: 1247,
  uniqueAttackers: 89,
  anomaliesDetected: 156,
  activeAlerts: 12,
  attackTypes: {
    'sql_injection': 456,
    'xss': 234,
    'brute_force': 189,
    'directory_traversal': 123,
    'automated_tool': 98,
    'other': 147,
  },
  severityBreakdown: {
    'critical': 23,
    'high': 67,
    'medium': 234,
    'low': 923,
  },
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Fetch analytics data (mock for now)
  const { data: analytics, isLoading, refetch } = useQuery(
    'dashboard-analytics',
    async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return mockAnalytics;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const StatCard: React.FC<{
    title: string;
    value: number;
    icon: React.ReactNode;
    color: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
    trend?: number;
    subtitle?: string;
  }> = ({ title, value, icon, color, trend, subtitle }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography color="textSecondary" gutterBottom variant="h6">
                {title}
              </Typography>
              <Typography variant="h4" component="h2" sx={{ fontWeight: 700 }}>
                {value.toLocaleString()}
              </Typography>
              {subtitle && (
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {subtitle}
                </Typography>
              )}
              {trend && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <TrendingUpIcon 
                    sx={{ 
                      fontSize: 16, 
                      color: trend > 0 ? 'success.main' : 'error.main',
                      mr: 0.5 
                    }} 
                  />
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: trend > 0 ? 'success.main' : 'error.main',
                      fontWeight: 500 
                    }}
                  >
                    {trend > 0 ? '+' : ''}{trend}% from last hour
                  </Typography>
                </Box>
              )}
            </Box>
            <Box
              sx={{
                backgroundColor: `${color}.main`,
                borderRadius: '50%',
                p: 1.5,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {icon}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (isLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            Security Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Real-time monitoring of AI Cybersecurity Honeypot
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={() => refetch()} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/reports')}
            startIcon={<InfoIcon />}
          >
            Generate Report
          </Button>
        </Box>
      </Box>

      {/* Security Warning */}
      <Alert 
        severity="warning" 
        sx={{ mb: 3 }}
        action={
          <Button color="inherit" size="small" href="/legal">
            View Legal Notice
          </Button>
        }
      >
        <strong>Educational Use Only:</strong> This honeypot system is designed for learning and research purposes. 
        Do not deploy to production environments.
      </Alert>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Attacks"
            value={analytics?.totalAttacks || 0}
            icon={<SecurityIcon sx={{ color: 'white', fontSize: 24 }} />}
            color="primary"
            trend={12.5}
            subtitle="Last 24 hours"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unique Attackers"
            value={analytics?.uniqueAttackers || 0}
            icon={<PeopleIcon sx={{ color: 'white', fontSize: 24 }} />}
            color="secondary"
            trend={-3.2}
            subtitle="Active sources"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Anomalies Detected"
            value={analytics?.anomaliesDetected || 0}
            icon={<WarningIcon sx={{ color: 'white', fontSize: 24 }} />}
            color="warning"
            trend={8.7}
            subtitle="ML-detected"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Alerts"
            value={analytics?.activeAlerts || 0}
            icon={<WarningIcon sx={{ color: 'white', fontSize: 24 }} />}
            color="error"
            trend={15.3}
            subtitle="Require attention"
          />
        </Grid>
      </Grid>

      {/* Attack Types Breakdown */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Attack Types Distribution
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {Object.entries(analytics?.attackTypes || {}).map(([type, count]) => {
                    const percentage = ((count as number) / (analytics?.totalAttacks || 1)) * 100;
                    const colors = {
                      'sql_injection': 'error',
                      'xss': 'warning',
                      'brute_force': 'info',
                      'directory_traversal': 'secondary',
                      'automated_tool': 'success',
                      'other': 'default',
                    } as const;
                    
                    return (
                      <Box key={type} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {type.replace('_', ' ')}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {count}
                            </Typography>
                            <Chip 
                              label={`${percentage.toFixed(1)}%`} 
                              size="small" 
                              color={colors[type as keyof typeof colors]}
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={percentage} 
                          color={colors[type as keyof typeof colors]}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    );
                  })}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Severity Breakdown
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {Object.entries(analytics?.severityBreakdown || {}).map(([severity, count]) => {
                    const percentage = ((count as number) / (analytics?.totalAttacks || 1)) * 100;
                    const colors = {
                      'critical': 'error',
                      'high': 'warning',
                      'medium': 'info',
                      'low': 'success',
                    } as const;
                    
                    return (
                      <Box key={severity} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize', fontWeight: 500 }}>
                            {severity}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {count}
                            </Typography>
                            <Chip 
                              label={`${percentage.toFixed(1)}%`} 
                              size="small" 
                              color={colors[severity as keyof typeof colors]}
                              variant="filled"
                            />
                          </Box>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={percentage} 
                          color={colors[severity as keyof typeof colors]}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                    );
                  })}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts and Tables */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <AttackTimeline />
          </motion.div>
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <TopAttackers />
          </motion.div>
        </Grid>

        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <AttackMap />
          </motion.div>
        </Grid>

        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <RecentAttacks />
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
