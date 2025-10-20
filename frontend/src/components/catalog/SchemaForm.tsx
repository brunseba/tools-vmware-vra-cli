import React, { useState, useMemo } from 'react'
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Switch,
  Typography,
  Button,
  Alert,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormHelperText,
  InputAdornment,
  Chip,
} from '@mui/material'
import {
  ExpandMore,
  Launch,
  Warning,
  CheckCircle,
  Info,
} from '@mui/icons-material'
import { CatalogItem, CatalogSchema } from '@/types/api'
import { useRequestCatalogItem } from '@/hooks/useCatalog'
import { useSettingsStore } from '@/store/settingsStore'

interface SchemaFormProps {
  item: CatalogItem
  schema?: CatalogSchema
  onClose: () => void
}

interface FormField {
  name: string
  type: string
  title?: string
  description?: string
  default?: any
  required: boolean
  enum?: string[]
  minimum?: number
  maximum?: number
  minLength?: number
  maxLength?: number
  pattern?: string
  properties?: Record<string, any>
}

export const SchemaForm: React.FC<SchemaFormProps> = ({
  item,
  schema,
  onClose,
}) => {
  const { settings } = useSettingsStore()
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [deploymentName, setDeploymentName] = useState('')
  const [reason, setReason] = useState('')
  
  const requestCatalogItemMutation = useRequestCatalogItem()

  // Parse schema into form fields
  const formFields = useMemo((): FormField[] => {
    if (!schema?.properties) return []
    
    return Object.entries(schema.properties).map(([name, prop]: [string, any]) => ({
      name,
      type: prop.type || 'string',
      title: prop.title || name,
      description: prop.description,
      default: prop.default,
      required: schema.required?.includes(name) || false,
      enum: prop.enum,
      minimum: prop.minimum,
      maximum: prop.maximum,
      minLength: prop.minLength,
      maxLength: prop.maxLength,
      pattern: prop.pattern,
      properties: prop.properties,
    }))
  }, [schema])

  // Initialize form data with defaults
  React.useEffect(() => {
    const initialData: Record<string, any> = {}
    formFields.forEach(field => {
      if (field.default !== undefined) {
        initialData[field.name] = field.default
      }
    })
    setFormData(initialData)
    
    // Set default deployment name
    if (!deploymentName) {
      const defaultName = item.name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-')
      setDeploymentName(`${defaultName}-${Date.now().toString().slice(-6)}`)
    }
  }, [formFields, item.name, deploymentName])

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }))
    
    // Clear validation error when user starts typing
    if (validationErrors[fieldName]) {
      setValidationErrors(prev => {
        const { [fieldName]: _, ...rest } = prev
        return rest
      })
    }
  }

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}
    
    // Validate required fields
    formFields.forEach(field => {
      const value = formData[field.name]
      
      if (field.required && (value === undefined || value === '' || value === null)) {
        errors[field.name] = `${field.title} is required`
        return
      }
      
      if (value !== undefined && value !== '') {
        // Type validation
        if (field.type === 'number' && isNaN(Number(value))) {
          errors[field.name] = `${field.title} must be a valid number`
        }
        
        if (field.type === 'integer' && (!Number.isInteger(Number(value)))) {
          errors[field.name] = `${field.title} must be an integer`
        }
        
        // Range validation
        if (field.minimum !== undefined && Number(value) < field.minimum) {
          errors[field.name] = `${field.title} must be at least ${field.minimum}`
        }
        
        if (field.maximum !== undefined && Number(value) > field.maximum) {
          errors[field.name] = `${field.title} must be at most ${field.maximum}`
        }
        
        // String length validation
        if (field.minLength !== undefined && String(value).length < field.minLength) {
          errors[field.name] = `${field.title} must be at least ${field.minLength} characters`
        }
        
        if (field.maxLength !== undefined && String(value).length > field.maxLength) {
          errors[field.name] = `${field.title} must be at most ${field.maxLength} characters`
        }
        
        // Pattern validation
        if (field.pattern && !new RegExp(field.pattern).test(String(value))) {
          errors[field.name] = `${field.title} format is invalid`
        }
      }
    })
    
    // Validate deployment name
    if (!deploymentName.trim()) {
      errors.deploymentName = 'Deployment name is required'
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      return
    }
    
    try {
      await requestCatalogItemMutation.mutateAsync({
        itemId: item.id,
        requestData: {
          item_id: item.id,
          project_id: settings.defaultProject || '',
          inputs: formData,
          name: deploymentName,
          reason: reason || `Deployment of ${item.name}`,
        },
      })
      
      onClose()
    } catch (error) {
      // Error handling is done in the mutation
    }
  }

  const renderFormField = (field: FormField) => {
    const value = formData[field.name] ?? ''
    const hasError = !!validationErrors[field.name]
    
    const commonProps = {
      fullWidth: true,
      margin: 'normal' as const,
      error: hasError,
      helperText: validationErrors[field.name] || field.description,
      required: field.required,
    }

    switch (field.type) {
      case 'boolean':
        return (
          <FormControlLabel
            key={field.name}
            control={
              <Switch
                checked={Boolean(value)}
                onChange={(e) => handleFieldChange(field.name, e.target.checked)}
              />
            }
            label={field.title}
            sx={{ mt: 2, mb: 1 }}
          />
        )

      case 'number':
      case 'integer':
        return (
          <TextField
            key={field.name}
            label={field.title}
            type="number"
            value={value}
            onChange={(e) => {
              const numValue = field.type === 'integer' ? parseInt(e.target.value) : parseFloat(e.target.value)
              handleFieldChange(field.name, isNaN(numValue) ? e.target.value : numValue)
            }}
            inputProps={{
              min: field.minimum,
              max: field.maximum,
              step: field.type === 'integer' ? 1 : 'any',
            }}
            {...commonProps}
          />
        )

      default:
        if (field.enum && field.enum.length > 0) {
          return (
            <FormControl key={field.name} {...commonProps}>
              <InputLabel>{field.title}</InputLabel>
              <Select
                value={value}
                label={field.title}
                onChange={(e) => handleFieldChange(field.name, e.target.value)}
              >
                {field.enum.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
              {(validationErrors[field.name] || field.description) && (
                <FormHelperText error={hasError}>
                  {validationErrors[field.name] || field.description}
                </FormHelperText>
              )}
            </FormControl>
          )
        }

        return (
          <TextField
            key={field.name}
            label={field.title}
            value={value}
            onChange={(e) => handleFieldChange(field.name, e.target.value)}
            multiline={field.maxLength && field.maxLength > 100}
            rows={field.maxLength && field.maxLength > 100 ? 3 : 1}
            inputProps={{
              minLength: field.minLength,
              maxLength: field.maxLength,
            }}
            {...commonProps}
          />
        )
    }
  }

  // Group fields by categories (if schema has nested objects)
  const requiredFields = formFields.filter(field => field.required)
  const optionalFields = formFields.filter(field => !field.required)

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Deploy {item.name}
      </Typography>

      {!settings.defaultProject && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          No default project configured. Please set a default project in settings.
        </Alert>
      )}

      {/* Basic deployment settings */}
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Deployment Name"
          value={deploymentName}
          onChange={(e) => setDeploymentName(e.target.value)}
          required
          error={!!validationErrors.deploymentName}
          helperText={validationErrors.deploymentName || 'Unique name for this deployment'}
          margin="normal"
        />

        <TextField
          fullWidth
          label="Reason (Optional)"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          multiline
          rows={2}
          placeholder="Business justification for this deployment..."
          margin="normal"
        />
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Schema fields */}
      {formFields.length === 0 ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Info />
            <Typography>
              This catalog item has no configurable parameters. Click Deploy to proceed with default settings.
            </Typography>
          </Box>
        </Alert>
      ) : (
        <>
          {/* Required fields */}
          {requiredFields.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Warning color="warning" />
                Required Parameters
              </Typography>
              {requiredFields.map(renderFormField)}
            </Box>
          )}

          {/* Optional fields in accordion */}
          {optionalFields.length > 0 && (
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  Optional Parameters ({optionalFields.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {optionalFields.map(renderFormField)}
              </AccordionDetails>
            </Accordion>
          )}
        </>
      )}

      {/* Summary */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Summary:</strong> Deploying "{item.name}" 
          {settings.defaultProject && ` to project "${settings.defaultProject}"`}
          {deploymentName && ` as "${deploymentName}"`}
        </Typography>
      </Alert>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button onClick={onClose} disabled={requestCatalogItemMutation.isPending}>
          Cancel
        </Button>
        <Button
          variant="contained"
          startIcon={<Launch />}
          onClick={handleSubmit}
          disabled={requestCatalogItemMutation.isPending || !settings.defaultProject}
          sx={{ minWidth: 120 }}
        >
          {requestCatalogItemMutation.isPending ? 'Deploying...' : 'Deploy'}
        </Button>
      </Box>
    </Box>
  )
}