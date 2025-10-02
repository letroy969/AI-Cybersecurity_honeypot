import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
} from '@mui/material';

const Reports: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, mb: 3 }}>
        Security Reports
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Generate and manage automated security reports and incident documentation.
      </Alert>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🚧 Under Construction
          </Typography>
          <Typography variant="body1" color="textSecondary">
            The reports page is currently being developed. It will include:
          </Typography>
          <ul>
            <li>Automated incident report generation</li>
            <li>Custom report templates</li>
            <li>PDF and HTML export options</li>
            <li>Scheduled report delivery</li>
            <li>Report archive and history</li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Reports;
