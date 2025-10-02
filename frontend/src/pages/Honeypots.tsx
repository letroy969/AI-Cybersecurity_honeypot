import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
} from '@mui/material';

const Honeypots: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
        Honeypot Management
      </Typography>
      
      <Alert severity="warning" sx={{ mb: 3 }}>
        Manage and monitor honeypot endpoints and configurations. All endpoints are simulated for educational purposes.
      </Alert>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🚧 Under Construction
          </Typography>
          <Typography variant="body1" color="textSecondary">
            The honeypots page is currently being developed. It will include:
          </Typography>
          <ul>
            <li>Honeypot endpoint status monitoring</li>
            <li>Configuration management</li>
            <li>Simulated service management</li>
            <li>Endpoint performance metrics</li>
            <li>Custom honeypot creation</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Honeypots;
