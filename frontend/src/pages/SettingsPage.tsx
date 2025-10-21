import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Save as SaveIcon,
  RestoreSharp as ResetIcon,
  Settings as SettingsIcon,
  Palette as PaletteIcon,
  Code as DevIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useSettingsStore } from '@/store/settingsStore';

export const SettingsPage: React.FC = () => {
  const {
    settings,
    theme,
    featureFlags,
    updateSettings,
    updateTheme,
    updateFeatureFlags,
    toggleDarkMode,
    addNotification,
  } = useSettingsStore();

  const [localSettings, setLocalSettings] = useState(settings);
  const [localTheme, setLocalTheme] = useState(theme);
  const [localFeatureFlags, setLocalFeatureFlags] = useState(featureFlags);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const handleSettingsChange = (field: keyof typeof settings, value: any) => {
    setLocalSettings(prev => ({ ...prev, [field]: value }));
    setHasUnsavedChanges(true);
  };

  const handleThemeChange = (field: keyof typeof theme, value: any) => {
    setLocalTheme(prev => ({ ...prev, [field]: value }));
    setHasUnsavedChanges(true);
  };

  const handleFeatureFlagChange = (field: keyof typeof featureFlags, value: boolean) => {
    setLocalFeatureFlags(prev => ({ ...prev, [field]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    updateSettings(localSettings);
    updateTheme(localTheme);
    updateFeatureFlags(localFeatureFlags);
    setHasUnsavedChanges(false);
    
    addNotification({
      type: 'success',
      title: 'Settings Saved',
      message: 'Your settings have been saved successfully.',
    });
  };

  const handleReset = () => {
    setLocalSettings(settings);
    setLocalTheme(theme);
    setLocalFeatureFlags(featureFlags);
    setHasUnsavedChanges(false);
    
    addNotification({
      type: 'info',
      title: 'Settings Reset',
      message: 'Changes have been discarded.',
    });
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <SettingsIcon color="primary" sx={{ fontSize: 32 }} />
        <Typography variant="h4" component="h1">
          Settings
        </Typography>
      </Box>

      {/* Unsaved Changes Alert */}
      {hasUnsavedChanges && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          You have unsaved changes. Don't forget to save them before leaving this page.
        </Alert>
      )}

      {/* Settings Sections */}
      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1 }}>
                <SettingsIcon color="primary" />
                <Typography variant="h6">General Settings</Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Default Project"
                    value={localSettings.defaultProject}
                    onChange={(e) => handleSettingsChange('defaultProject', e.target.value)}
                    helperText="Default vRA project for deployments and catalog items"
                    placeholder="e.g., my-project-id"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Page Size"
                    type="number"
                    value={localSettings.pageSize}
                    onChange={(e) => handleSettingsChange('pageSize', parseInt(e.target.value) || 25)}
                    inputProps={{ min: 10, max: 1000 }}
                    helperText="Number of items per page"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Refresh Interval (ms)"
                    type="number"
                    value={localSettings.refreshInterval}
                    onChange={(e) => handleSettingsChange('refreshInterval', parseInt(e.target.value) || 30000)}
                    inputProps={{ min: 5000, max: 300000 }}
                    helperText="Auto-refresh interval"
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localSettings.autoRefresh}
                        onChange={(e) => handleSettingsChange('autoRefresh', e.target.checked)}
                      />
                    }
                    label="Auto-refresh data"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Theme Settings */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1 }}>
                <PaletteIcon color="primary" />
                <Typography variant="h6">Theme & Appearance</Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localTheme.mode === 'dark'}
                        onChange={(e) => {
                          const newMode = e.target.checked ? 'dark' : 'light';
                          handleThemeChange('mode', newMode);
                        }}
                      />
                    }
                    label="Dark Mode"
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Primary Color"
                    value={localTheme.primaryColor}
                    onChange={(e) => handleThemeChange('primaryColor', e.target.value)}
                    type="color"
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Secondary Color"
                    value={localTheme.secondaryColor}
                    onChange={(e) => handleThemeChange('secondaryColor', e.target.value)}
                    type="color"
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Font Size</InputLabel>
                    <Select
                      value={localTheme.fontSize}
                      label="Font Size"
                      onChange={(e) => handleThemeChange('fontSize', e.target.value)}
                    >
                      <MenuItem value="small">Small</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="large">Large</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Feature Flags */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1 }}>
                <DevIcon color="primary" />
                <Typography variant="h6">Feature Flags</Typography>
                <Tooltip title="Enable or disable specific application features">
                  <IconButton size="small">
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFeatureFlags.enableReports}
                        onChange={(e) => handleFeatureFlagChange('enableReports', e.target.checked)}
                      />
                    }
                    label="Reports & Analytics"
                  />
                </Grid>

                <Grid item xs={12} sm={6} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFeatureFlags.enableWorkflows}
                        onChange={(e) => handleFeatureFlagChange('enableWorkflows', e.target.checked)}
                      />
                    }
                    label="Workflow Management"
                  />
                </Grid>

                <Grid item xs={12} sm={6} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFeatureFlags.enableBulkOperations}
                        onChange={(e) => handleFeatureFlagChange('enableBulkOperations', e.target.checked)}
                      />
                    }
                    label="Bulk Operations"
                  />
                </Grid>

                <Grid item xs={12} sm={6} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFeatureFlags.enableRealTimeUpdates}
                        onChange={(e) => handleFeatureFlagChange('enableRealTimeUpdates', e.target.checked)}
                      />
                    }
                    label="Real-time Updates"
                  />
                </Grid>

                <Grid item xs={12} sm={6} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={localFeatureFlags.enableExport}
                        onChange={(e) => handleFeatureFlagChange('enableExport', e.target.checked)}
                      />
                    }
                    label="Data Export"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Advanced Settings */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Advanced Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="API Base URL"
                    value={localSettings.apiBaseUrl}
                    onChange={(e) => handleSettingsChange('apiBaseUrl', e.target.value)}
                    helperText="Base URL for API requests (usually /api)"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          startIcon={<ResetIcon />}
          onClick={handleReset}
          disabled={!hasUnsavedChanges}
        >
          Reset Changes
        </Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={!hasUnsavedChanges}
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default SettingsPage;