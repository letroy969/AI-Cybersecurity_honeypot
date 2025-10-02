import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Tooltip,
} from '@mui/material';
import {
  Public as PublicIcon,
  LocationOn as LocationIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Mock geographic data
const mockGeoData = [
  { country: 'United States', region: 'California', city: 'San Francisco', attacks: 234, severity: 'high', flag: '🇺🇸' },
  { country: 'China', region: 'Beijing', city: 'Beijing', attacks: 189, severity: 'high', flag: '🇨🇳' },
  { country: 'Russia', region: 'Moscow', city: 'Moscow', attacks: 156, severity: 'critical', flag: '🇷🇺' },
  { country: 'Germany', region: 'Berlin', city: 'Berlin', attacks: 123, severity: 'medium', flag: '🇩🇪' },
  { country: 'United Kingdom', region: 'London', city: 'London', attacks: 98, severity: 'medium', flag: '🇬🇧' },
  { country: 'Japan', region: 'Tokyo', city: 'Tokyo', attacks: 87, severity: 'low', flag: '🇯🇵' },
  { country: 'Brazil', region: 'São Paulo', city: 'São Paulo', attacks: 76, severity: 'medium', flag: '🇧🇷' },
  { country: 'India', region: 'Mumbai', city: 'Mumbai', attacks: 65, severity: 'low', flag: '🇮🇳' },
];

const AttackMap: React.FC = () => {
  const totalAttacks = mockGeoData.reduce((sum, item) => sum + item.attacks, 0);
  const totalCountries = mockGeoData.length;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <PublicIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Geographic Distribution
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              <Chip
                label={`${totalAttacks} attacks`}
                color="primary"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`${totalCountries} countries`}
                color="secondary"
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>
        </Box>

        {/* Simple map visualization */}
        <Box sx={{ 
          height: 200, 
          backgroundColor: 'background.paper', 
          borderRadius: 2, 
          mb: 2,
          position: 'relative',
          overflow: 'hidden',
          border: '1px solid',
          borderColor: 'divider'
        }}>
          {/* Mock world map representation */}
          <Box sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: '4rem',
            opacity: 0.1,
            userSelect: 'none'
          }}>
            🌍
          </Box>
          
          {/* Attack markers */}
          {mockGeoData.slice(0, 5).map((item, index) => (
            <motion.div
              key={item.country}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              style={{
                position: 'absolute',
                top: `${20 + index * 15}%`,
                left: `${30 + (index % 2) * 40}%`,
              }}
            >
              <Tooltip title={`${item.country}: ${item.attacks} attacks`}>
                <Box
                  sx={{
                    width: Math.max(8, item.attacks / 10),
                    height: Math.max(8, item.attacks / 10),
                    backgroundColor: getSeverityColor(item.severity) === 'error' ? '#ef4444' :
                                  getSeverityColor(item.severity) === 'warning' ? '#f59e0b' :
                                  getSeverityColor(item.severity) === 'info' ? '#3b82f6' : '#10b981',
                    borderRadius: '50%',
                    border: '2px solid white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                    cursor: 'pointer',
                  }}
                />
              </Tooltip>
            </motion.div>
          ))}
        </Box>

        {/* Top countries list */}
        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'text.secondary' }}>
            Top Attack Sources
          </Typography>
          <List dense>
            {mockGeoData.slice(0, 6).map((item, index) => (
              <motion.div
                key={item.country}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <ListItem sx={{ px: 0, py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <Typography sx={{ fontSize: '1.2rem' }}>
                      {item.flag}
                    </Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {item.country}
                        </Typography>
                        <Chip
                          label={item.attacks}
                          size="small"
                          color={getSeverityColor(item.severity)}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="caption" color="textSecondary">
                        {item.city}, {item.region}
                      </Typography>
                    }
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>
        </Box>

        {/* Security insights */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.8 }}
        >
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            backgroundColor: 'info.dark', 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'info.main'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <SecurityIcon sx={{ color: 'white', fontSize: 16 }} />
              <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
                Geographic Insights
              </Typography>
            </Box>
            <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
              • {mockGeoData[0].country} accounts for {Math.round((mockGeoData[0].attacks / totalAttacks) * 100)}% of attacks
            </Typography>
            <Typography variant="caption" sx={{ color: 'white', display: 'block' }}>
              • Peak activity from {mockGeoData.filter(item => item.severity === 'critical' || item.severity === 'high').length} high-risk regions
            </Typography>
          </Box>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export default AttackMap;
