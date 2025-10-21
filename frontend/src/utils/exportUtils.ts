import { format as formatDate } from 'date-fns';

export interface ExportData {
  filename: string;
  data: any[];
  headers?: string[];
  title?: string;
  subtitle?: string;
}

// CSV Export functionality
export const exportToCSV = (exportData: ExportData) => {
  const { filename, data, headers } = exportData;
  
  if (!data || data.length === 0) {
    throw new Error('No data available for export');
  }

  // Generate headers from first data object if not provided
  const csvHeaders = headers || Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    // Headers row
    csvHeaders.join(','),
    // Data rows
    ...data.map(row => 
      csvHeaders.map(header => {
        const value = row[header];
        // Handle values that might contain commas, quotes, or newlines
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value || '';
      }).join(',')
    )
  ].join('\n');

  // Create and download file
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
};

// JSON Export functionality
export const exportToJSON = (exportData: ExportData) => {
  const { filename, data, title, subtitle } = exportData;
  
  if (!data || data.length === 0) {
    throw new Error('No data available for export');
  }

  const jsonContent = {
    metadata: {
      title: title || 'Data Export',
      subtitle: subtitle || '',
      exportDate: new Date().toISOString(),
      totalRecords: data.length,
    },
    data,
  };

  const blob = new Blob([JSON.stringify(jsonContent, null, 2)], { 
    type: 'application/json;charset=utf-8;' 
  });
  
  const link = document.createElement('a');
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
};

// Basic PDF export using HTML to PDF conversion
export const exportToPDF = async (exportData: ExportData) => {
  const { filename, data, title, subtitle } = exportData;
  
  if (!data || data.length === 0) {
    throw new Error('No data available for export');
  }

  // Create HTML content for PDF
  const headers = Object.keys(data[0]);
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>${title || 'Export Report'}</title>
      <style>
        body { 
          font-family: Arial, sans-serif; 
          margin: 20px;
          font-size: 12px;
        }
        h1 { 
          color: #1976d2; 
          border-bottom: 2px solid #1976d2;
          padding-bottom: 10px;
        }
        h2 { 
          color: #666; 
          font-size: 14px;
          margin-bottom: 20px;
        }
        table { 
          border-collapse: collapse; 
          width: 100%; 
          margin-top: 20px;
        }
        th, td { 
          border: 1px solid #ddd; 
          padding: 8px; 
          text-align: left;
          word-wrap: break-word;
        }
        th { 
          background-color: #f5f5f5; 
          font-weight: bold;
        }
        tr:nth-child(even) { 
          background-color: #f9f9f9; 
        }
        .metadata {
          font-size: 10px;
          color: #666;
          margin-bottom: 20px;
        }
        .page-break {
          page-break-after: always;
        }
      </style>
    </head>
    <body>
      <h1>${title || 'Data Export Report'}</h1>
      ${subtitle ? `<h2>${subtitle}</h2>` : ''}
      
      <div class="metadata">
        <p>Generated on: ${formatDate(new Date(), 'PPpp')}</p>
        <p>Total records: ${data.length}</p>
      </div>

      <table>
        <thead>
          <tr>
            ${headers.map(header => `<th>${header}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${data.map(row => `
            <tr>
              ${headers.map(header => `<td>${row[header] || ''}</td>`).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    </body>
    </html>
  `;

  // Use browser's print functionality to generate PDF
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    
    // Wait for content to load before printing
    printWindow.addEventListener('load', () => {
      printWindow.focus();
      printWindow.print();
      
      // Close the window after a delay to allow printing to complete
      setTimeout(() => {
        printWindow.close();
      }, 1000);
    });
  }
};

// Export deployment data with proper formatting
export const exportDeploymentData = (deployments: any[], format: 'csv' | 'json' | 'pdf' = 'csv') => {
  const processedData = deployments.map(deployment => ({
    'Deployment ID': deployment.id,
    'Name': deployment.name,
    'Status': deployment.status,
    'Project ID': deployment.projectId,
    'Owner': deployment.inputs?.owner || 'N/A',
    'Created': formatDate(new Date(deployment.createdAt), 'yyyy-MM-dd HH:mm:ss'),
    'Completed': deployment.completedAt ? formatDate(new Date(deployment.completedAt), 'yyyy-MM-dd HH:mm:ss') : 'N/A',
  }));

  const exportData: ExportData = {
    filename: `deployments_export_${formatDate(new Date(), 'yyyy-MM-dd_HHmm')}`,
    data: processedData,
    title: 'VMware vRA Deployments Report',
    subtitle: `Exported ${deployments.length} deployment(s)`,
  };

  switch (format) {
    case 'csv':
      return exportToCSV(exportData);
    case 'json':
      return exportToJSON(exportData);
    case 'pdf':
      return exportToPDF(exportData);
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
};

// Export analytics/reports data
export const exportAnalyticsData = (
  stats: any, 
  timeRange: string, 
  format: 'csv' | 'json' | 'pdf' = 'csv'
) => {
  const processedData = [
    {
      'Metric': 'Total Deployments',
      'Value': stats.totalDeployments,
      'Period': timeRange,
    },
    {
      'Metric': 'Active Deployments',
      'Value': stats.activeDeployments,
      'Period': timeRange,
    },
    {
      'Metric': 'Failed Deployments',
      'Value': stats.failedDeployments,
      'Period': timeRange,
    },
    {
      'Metric': 'Total Users',
      'Value': stats.totalUsers,
      'Period': timeRange,
    },
  ];

  const exportData: ExportData = {
    filename: `analytics_report_${formatDate(new Date(), 'yyyy-MM-dd_HHmm')}`,
    data: processedData,
    title: 'VMware vRA Analytics Report',
    subtitle: `Analytics data for ${timeRange}`,
  };

  switch (format) {
    case 'csv':
      return exportToCSV(exportData);
    case 'json':
      return exportToJSON(exportData);
    case 'pdf':
      return exportToPDF(exportData);
    default:
      throw new Error(`Unsupported export format: ${format}`);
  }
};

// Utility to format file size
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Utility to validate export data
export const validateExportData = (data: any[]): boolean => {
  return Array.isArray(data) && data.length > 0 && typeof data[0] === 'object';
};