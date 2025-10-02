import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import {
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Mock timeline data
const mockTimelineData = [
  { time: '00:00', attacks: 12, anomalies: 2, attackers: 8 },
  { time: '01:00', attacks: 8, anomalies: 1, attackers: 5 },
  { time: '02:00', attacks: 15, anomalies: 3, attackers: 9 },
  { time: '03:00', attacks: 23, anomalies: 5, attackers: 12 },
  { time: '04:00', attacks: 18, anomalies: 2, attackers: 10 },
  { time: '05:00', attacks: 25, anomalies: 4, attackers: 14 },
  { time: '06:00', attacks: 32, anomalies: 6, attackers: 18 },
  { time: '07:00', attacks: 28, anomalies: 3, attackers: 15 },
  { time: '08:00', attacks: 45, anomalies: 8, attackers: 22 },
  { time: '09:00', attacks: 52, anomalies: 12, attackers: 28 },
  { time: '10:00', attacks: 38, anomalies: 7, attackers: 20 },
  { time: '11:00', attacks: 41, anomalies: 9, attackers: 24 },
  { time: '12:00', attacks: 48, anomalies: 11, attackers: 26 },
  { time: '13:00', attacks: 35, anomalies: 6, attackers: 19 },
  { time: '14:00', attacks: 42, anomalies: 8, attackers: 23 },
  { time: '15:00', attacks: 55, anomalies: 13, attackers: 30 },
  { time: '16:00', attacks: 38, anomalies: 7, attackers: 21 },
  { time: '17:00', attacks: 29, anomalies: 4, attackers: 16 },
  { time: '18:00', attacks: 33, anomalies: 6, attackers: 18 },
  { time: '19:00', attacks: 41, anomalies: 9, attackers: 22 },
  { time: '20:00', attacks: 37, anomalies: 8, attackers: 20 },
  { time: '21:00', attacks: 31, anomalies: 5, attackers: 17 },
  { time: '22:00', attacks: 26, anomalies: 4, attackers: 14 },
  { time: '23:00', attacks: 19, anomalies: 3, attackers: 11 },
];

const AttackTimeline: React.FC = () => {
  const totalAttacks = mockTimelineData.reduce((sum, data) => sum + data.attacks, 0);
  const totalAnomalies = mockTimelineData.reduce((sum, data) => sum + data.anomalies, 0);
  const avgAttackersPerHour = mockTimelineData.reduce((sum, data) => sum + data.attackers, 0) / mockTimelineData.length;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
              Attack Timeline
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip
                icon={<TrendingUpIcon />}
                label={`${totalAttacks} total attacks`}
                color="primary"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`${totalAnomalies} anomalies`}
                color="warning"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`${avgAttackersPerHour.toFixed(1)} avg attackers/hour`}
                color="info"
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>
          <Tooltip title="Refresh Timeline">
            <IconButton size="small" color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Box sx={{ height: 300, mt: 2 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={mockTimelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#94a3b8"
                fontSize={12}
                tick={{ fill: '#94a3b8' }}
              />
              <YAxis 
                stroke="#94a3b8"
                fontSize={12}
                tick={{ fill: '#94a3b8' }}
              />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#ffffff',
                }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Area
                type="monotone"
                dataKey="attacks"
                stroke="#ef4444"
                fill="#ef4444"
                fillOpacity={0.3}
                strokeWidth={2}
                name="Total Attacks"
              />
              <Area
                type="monotone"
                dataKey="anomalies"
                stroke="#f59e0b"
                fill="#f59e0b"
                fillOpacity={0.3}
                strokeWidth={2}
                name="Anomalies"
              />
              <Line
                type="monotone"
                dataKey="attackers"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
                name="Unique Attackers"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>

        {/* Legend */}
        <Box sx={{ display: 'flex', gap: 2, mt: 2, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 12, backgroundColor: '#ef4444', borderRadius: '2px' }} />
            <Typography variant="caption" color="textSecondary">
              Total Attacks
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 12, backgroundColor: '#f59e0b', borderRadius: '2px' }} />
            <Typography variant="caption" color="textSecondary">
              Anomalies
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 2, backgroundColor: '#3b82f6' }} />
            <Typography variant="caption" color="textSecondary">
              Unique Attackers
            </Typography>
          </Box>
        </Box>

        {/* Peak Activity Alert */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.5 }}
        >
          <Box sx={{ 
            mt: 2, 
            p: 2, 
            backgroundColor: 'warning.dark', 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'warning.main'
          }}>
            <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
              🚨 Peak Activity Detected
            </Typography>
            <Typography variant="caption" sx={{ color: 'white', display: 'block', mt: 0.5 }}>
              Highest attack volume: 55 attacks at 15:00 (13 anomalies detected)
            </Typography>
          </Box>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export default AttackTimeline;
