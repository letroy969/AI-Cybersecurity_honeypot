import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Security as SecurityIcon,
  BugReport as BugReportIcon,
  Schedule as ScheduleIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Mock recent attacks data
const mockRecentAttacks = [
  {
    id: 1,
    timestamp: '2 minutes ago',
    sourceIp: '192.168.1.100',
    endpoint: '/api/honeypots/login',
    method: 'POST',
    attackType: 'brute_force',
    severity: 'high',
    country: 'United States',
    flag: '🇺🇸',
    userAgent: 'sqlmap/1.0',
    anomalyScore: 0.92,
    statusCode: 401,
  },
  {
    id: 2,
    timestamp: '5 minutes ago',
    sourceIp: '10.0.0.45',
    endpoint: '/api/honeypots/sql',
    method: 'GET',
    attackType: 'sql_injection',
    severity: 'critical',
    country: 'China',
    flag: '🇨🇳',
    userAgent: 'Mozilla/5.0 (compatible; Nmap Scripting Engine)',
    anomalyScore: 0.89,
    statusCode: 200,
  },
  {
    id: 3,
    timestamp: '8 minutes ago',
    sourceIp: '172.16.0.78',
    endpoint: '/api/honeypots/file',
    method: 'GET',
    attackType: 'directory_traversal',
    severity: 'high',
    country: 'Russia',
    flag: '🇷🇺',
    userAgent: 'Nikto/2.1.6',
    anomalyScore: 0.95,
    statusCode: 200,
  },
  {
    id: 4,
    timestamp: '12 minutes ago',
    sourceIp: '203.0.113.12',
    endpoint: '/api/honeypots/config',
    method: 'GET',
    attackType: 'information_disclosure',
    severity: 'medium',
    country: 'Germany',
    flag: '🇩🇪',
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    anomalyScore: 0.67,
    statusCode: 200,
  },
  {
    id: 5,
    timestamp: '15 minutes ago',
    sourceIp: '198.51.100.34',
    endpoint: '/api/honeypots/admin',
    method: 'POST',
    attackType: 'xss',
    severity: 'medium',
    country: 'United Kingdom',
    flag: '🇬🇧',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    anomalyScore: 0.74,
    statusCode: 400,
  },
];

const RecentAttacks: React.FC = () => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getAttackTypeColor = (type: string) => {
    const colors = {
      'sql_injection': 'error',
      'xss': 'warning',
      'brute_force': 'info',
      'directory_traversal': 'secondary',
      'information_disclosure': 'info',
    };
    return colors[type as keyof typeof colors] || 'default';
  };

  const getStatusCodeColor = (status: number) => {
    if (status >= 500) return 'error';
    if (status >= 400) return 'warning';
    if (status >= 300) return 'info';
    return 'success';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar sx={{ bgcolor: 'error.main' }}>
            <BugReportIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Recent Attacks
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Latest security incidents
            </Typography>
          </Box>
          <Tooltip title="View all attacks">
            <IconButton size="small">
              <OpenInNewIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <List sx={{ p: 0 }}>
          {mockRecentAttacks.map((attack, index) => (
            <motion.div
              key={attack.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <ListItem sx={{ px: 0, py: 1.5 }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <Avatar sx={{ 
                    width: 32, 
                    height: 32, 
                    bgcolor: getSeverityColor(attack.severity) + '.main',
                    fontSize: '0.75rem'
                  }}>
                    {attack.method}
                  </Avatar>
                </ListItemIcon>
                
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                        {attack.sourceIp}
                      </Typography>
                      <Typography sx={{ fontSize: '0.9rem' }}>
                        {attack.flag}
                      </Typography>
                      <Chip
                        label={attack.severity}
                        size="small"
                        color={getSeverityColor(attack.severity)}
                        variant="filled"
                      />
                      <Chip
                        label={`${(attack.anomalyScore * 100).toFixed(0)}%`}
                        size="small"
                        color="warning"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Chip
                          label={attack.attackType.replace('_', ' ')}
                          size="small"
                          color={getAttackTypeColor(attack.attackType)}
                          variant="outlined"
                        />
                        <Chip
                          label={`${attack.method} ${attack.endpoint}`}
                          size="small"
                          variant="outlined"
                          sx={{ fontFamily: 'monospace', fontSize: '0.7rem' }}
                        />
                        <Chip
                          label={attack.statusCode}
                          size="small"
                          color={getStatusCodeColor(attack.statusCode)}
                          variant="outlined"
                        />
                      </Box>

                      <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 0.5 }}>
                        {attack.userAgent.length > 50 ? 
                          `${attack.userAgent.substring(0, 50)}...` : 
                          attack.userAgent
                        }
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ScheduleIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
                        <Typography variant="caption" color="textSecondary">
                          {attack.timestamp}
                        </Typography>
                      </Box>
                    </Box>
                  }
                />
              </ListItem>
              
              {index < mockRecentAttacks.length - 1 && (
                <Divider sx={{ ml: 6 }} />
              )}
            </motion.div>
          ))}
        </List>

        {/* Alert summary */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.6 }}
        >
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            backgroundColor: 'error.dark', 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'error.main'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <SecurityIcon sx={{ color: 'white', fontSize: 16 }} />
              <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
                Active Threats
              </Typography>
            </Box>
            <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
              • {mockRecentAttacks.filter(a => a.severity === 'critical').length} critical attacks in last 15 minutes
            </Typography>
            <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
              • {mockRecentAttacks.filter(a => a.anomalyScore > 0.8).length} high-confidence anomalies detected
            </Typography>
          </Box>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export default RecentAttacks;
