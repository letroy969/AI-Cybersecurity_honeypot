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
  LinearProgress,
} from '@mui/material';
import {
  Person as PersonIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Mock attacker data
const mockAttackers = [
  {
    id: 1,
    ip: '192.168.1.100',
    country: 'United States',
    flag: '🇺🇸',
    attackCount: 156,
    uniqueEndpoints: 23,
    attackTypes: ['sql_injection', 'xss', 'brute_force'],
    maxSeverity: 'critical',
    lastSeen: '2 minutes ago',
    riskScore: 92,
    isBot: true,
  },
  {
    id: 2,
    ip: '10.0.0.45',
    country: 'China',
    flag: '🇨🇳',
    attackCount: 134,
    uniqueEndpoints: 18,
    attackTypes: ['directory_traversal', 'automated_tool'],
    maxSeverity: 'high',
    lastSeen: '5 minutes ago',
    riskScore: 87,
    isBot: true,
  },
  {
    id: 3,
    ip: '172.16.0.78',
    country: 'Russia',
    flag: '🇷🇺',
    attackCount: 98,
    uniqueEndpoints: 15,
    attackTypes: ['sql_injection', 'brute_force'],
    maxSeverity: 'high',
    lastSeen: '8 minutes ago',
    riskScore: 78,
    isBot: false,
  },
  {
    id: 4,
    ip: '203.0.113.12',
    country: 'Germany',
    flag: '🇩🇪',
    attackCount: 76,
    uniqueEndpoints: 12,
    attackTypes: ['xss', 'automated_tool'],
    maxSeverity: 'medium',
    lastSeen: '12 minutes ago',
    riskScore: 65,
    isBot: true,
  },
  {
    id: 5,
    ip: '198.51.100.34',
    country: 'United Kingdom',
    flag: '🇬🇧',
    attackCount: 54,
    uniqueEndpoints: 9,
    attackTypes: ['directory_traversal'],
    maxSeverity: 'medium',
    lastSeen: '15 minutes ago',
    riskScore: 58,
    isBot: false,
  },
];

const TopAttackers: React.FC = () => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'error';
    if (score >= 60) return 'warning';
    if (score >= 40) return 'info';
    return 'success';
  };

  const getAttackTypeColor = (type: string) => {
    const colors = {
      'sql_injection': 'error',
      'xss': 'warning',
      'brute_force': 'info',
      'directory_traversal': 'secondary',
      'automated_tool': 'success',
    };
    return colors[type as keyof typeof colors] || 'default';
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar sx={{ bgcolor: 'secondary.main' }}>
            <SecurityIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Top Attackers
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Most active threat sources
            </Typography>
          </Box>
          <Tooltip title="View all attackers">
            <IconButton size="small">
              <MoreVertIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <List sx={{ p: 0 }}>
          {mockAttackers.map((attacker, index) => (
            <motion.div
              key={attacker.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <ListItem sx={{ px: 0, py: 1.5, borderBottom: index < mockAttackers.length - 1 ? '1px solid' : 'none', borderColor: 'divider' }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <Avatar sx={{ width: 32, height: 32, bgcolor: getRiskColor(attacker.riskScore) + '.main' }}>
                    <PersonIcon sx={{ fontSize: 18 }} />
                  </Avatar>
                </ListItemIcon>
                
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                        {attacker.ip}
                      </Typography>
                      <Typography sx={{ fontSize: '1rem' }}>
                        {attacker.flag}
                      </Typography>
                      {attacker.isBot && (
                        <Chip label="Bot" size="small" color="warning" variant="outlined" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Chip
                          label={`${attacker.attackCount} attacks`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                        <Chip
                          label={`${attacker.uniqueEndpoints} endpoints`}
                          size="small"
                          color="info"
                          variant="outlined"
                        />
                        <Chip
                          label={attacker.maxSeverity}
                          size="small"
                          color={getSeverityColor(attacker.maxSeverity)}
                          variant="filled"
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                        {attacker.attackTypes.slice(0, 2).map((type) => (
                          <Chip
                            key={type}
                            label={type.replace('_', ' ')}
                            size="small"
                            color={getAttackTypeColor(type)}
                            variant="outlined"
                          />
                        ))}
                        {attacker.attackTypes.length > 2 && (
                          <Typography variant="caption" color="textSecondary">
                            +{attacker.attackTypes.length - 2} more
                          </Typography>
                        )}
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" color="textSecondary">
                              Risk Score
                            </Typography>
                            <Typography variant="caption" sx={{ fontWeight: 500 }}>
                              {attacker.riskScore}/100
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={attacker.riskScore}
                            color={getRiskColor(attacker.riskScore)}
                            sx={{ height: 4, borderRadius: 2 }}
                          />
                        </Box>
                      </Box>

                      <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                        Last seen: {attacker.lastSeen}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            </motion.div>
          ))}
        </List>

        {/* Summary stats */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.6 }}
        >
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            backgroundColor: 'warning.dark', 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'warning.main'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <WarningIcon sx={{ color: 'white', fontSize: 16 }} />
              <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
                Threat Assessment
              </Typography>
            </Box>
            <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
              • {mockAttackers.filter(a => a.isBot).length}/{mockAttackers.length} confirmed bot activity
            </Typography>
            <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
              • {mockAttackers.filter(a => a.riskScore >= 80).length} high-risk sources identified
            </Typography>
          </Box>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export default TopAttackers;
