import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
} from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
        System Settings
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Configure system settings, notifications, and security parameters.
      </Alert>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🚧 Under Construction
          </Typography>
          <Typography variant="body1" color="textSecondary">
            The settings page is currently being developed. It will include:
          </Typography>
          <ul>
            <li>System configuration options</li>
            <li>Alert and notification settings</li>
            <li>Security threshold configuration</li>
            <li>User preferences and themes</li>
            <li>Data retention policies</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings;
