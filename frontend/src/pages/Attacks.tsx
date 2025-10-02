import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
} from '@mui/material';

const Attacks: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
        Attack Events
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This page will display detailed attack event logs and analysis. 
        Features include filtering, searching, and detailed attack forensics.
      </Alert>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🚧 Under Construction
          </Typography>
          <Typography variant="body1" color="textSecondary">
            The attacks page is currently being developed. It will include:
          </Typography>
          <ul>
            <li>Real-time attack event logs</li>
            <li>Advanced filtering and search capabilities</li>
            <li>Attack timeline visualization</li>
            <li>Detailed attack forensics</li>
            <li>Export functionality</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Attacks;
