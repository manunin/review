import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Upload as UploadIcon,
  Reviews as ReviewsIcon,
  Home as HomeIcon,
} from '@mui/icons-material';

const Header = () => {
  const location = useLocation();

  const navItems = [
    { label: 'Home', path: '/', icon: <HomeIcon /> },
    { label: 'Upload', path: '/upload', icon: <UploadIcon /> },
    { label: 'Reviews', path: '/reviews', icon: <ReviewsIcon /> },
    { label: 'Analytics', path: '/analytics', icon: <AnalyticsIcon /> },
  ];

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          🔍 Smart Review Analyzer
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              component={Link}
              to={item.path}
              color="inherit"
              startIcon={item.icon}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
