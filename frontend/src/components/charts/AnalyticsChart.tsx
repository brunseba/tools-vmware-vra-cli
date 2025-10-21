import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Box, useTheme } from '@mui/material';
import { format, subDays } from 'date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

export type ChartType = 'line' | 'bar' | 'doughnut';

interface AnalyticsChartProps {
  type: ChartType;
  data: any;
  options?: any;
  height?: number;
  timeRange?: string;
}

// Generate sample data based on time range
const generateTimeSeriesData = (timeRange: string, metric: string) => {
  const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365;
  const labels = Array.from({ length: days }, (_, i) => 
    format(subDays(new Date(), days - 1 - i), days <= 30 ? 'MMM dd' : 'MMM yyyy')
  );

  const baseValues = {
    deployments: Array.from({ length: days }, () => Math.floor(Math.random() * 20) + 5),
    successes: Array.from({ length: days }, () => Math.floor(Math.random() * 18) + 4),
    failures: Array.from({ length: days }, () => Math.floor(Math.random() * 3) + 1),
  };

  return { labels, values: baseValues };
};

// Status distribution data
const statusDistributionData = {
  labels: ['Running', 'Creating', 'Failed', 'Stopped'],
  datasets: [
    {
      data: [89, 12, 8, 15],
      backgroundColor: [
        'rgba(76, 175, 80, 0.8)',   // Green for Running
        'rgba(33, 150, 243, 0.8)',  // Blue for Creating
        'rgba(244, 67, 54, 0.8)',   // Red for Failed
        'rgba(158, 158, 158, 0.8)',  // Gray for Stopped
      ],
      borderColor: [
        'rgba(76, 175, 80, 1)',
        'rgba(33, 150, 243, 1)',
        'rgba(244, 67, 54, 1)',
        'rgba(158, 158, 158, 1)',
      ],
      borderWidth: 2,
    },
  ],
};

export const AnalyticsChart: React.FC<AnalyticsChartProps> = ({
  type,
  data,
  options: customOptions,
  height = 300,
  timeRange = '30d',
}) => {
  const theme = useTheme();
  
  // Generate sample time series data
  const timeSeriesData = generateTimeSeriesData(timeRange, 'deployments');
  
  // Default chart options with theme integration
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: theme.palette.text.primary,
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: theme.palette.background.paper,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.secondary,
        borderColor: theme.palette.divider,
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        intersect: false,
        mode: 'index' as const,
      },
    },
    scales: type !== 'doughnut' ? {
      x: {
        grid: {
          color: theme.palette.divider,
          borderColor: theme.palette.divider,
        },
        ticks: {
          color: theme.palette.text.secondary,
        },
      },
      y: {
        grid: {
          color: theme.palette.divider,
          borderColor: theme.palette.divider,
        },
        ticks: {
          color: theme.palette.text.secondary,
        },
        beginAtZero: true,
      },
    } : {},
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6,
      },
      line: {
        tension: 0.3,
      },
    },
  };

  // Merge custom options with defaults
  const chartOptions = { ...defaultOptions, ...customOptions };

  // Default datasets for different chart types
  const getDefaultData = () => {
    if (type === 'doughnut') {
      return statusDistributionData;
    }

    return {
      labels: timeSeriesData.labels,
      datasets: [
        {
          label: 'Successful Deployments',
          data: timeSeriesData.values.successes,
          backgroundColor: type === 'bar' 
            ? 'rgba(76, 175, 80, 0.8)' 
            : 'rgba(76, 175, 80, 0.1)',
          borderColor: 'rgba(76, 175, 80, 1)',
          borderWidth: 2,
          fill: type === 'line',
          tension: 0.3,
        },
        {
          label: 'Failed Deployments',
          data: timeSeriesData.values.failures,
          backgroundColor: type === 'bar' 
            ? 'rgba(244, 67, 54, 0.8)' 
            : 'rgba(244, 67, 54, 0.1)',
          borderColor: 'rgba(244, 67, 54, 1)',
          borderWidth: 2,
          fill: type === 'line',
          tension: 0.3,
        },
      ],
    };
  };

  const chartData = data || getDefaultData();

  const renderChart = () => {
    switch (type) {
      case 'line':
        return <Line data={chartData} options={chartOptions} />;
      case 'bar':
        return <Bar data={chartData} options={chartOptions} />;
      case 'doughnut':
        return <Doughnut data={chartData} options={chartOptions} />;
      default:
        return <Line data={chartData} options={chartOptions} />;
    }
  };

  return (
    <Box sx={{ height, position: 'relative' }}>
      {renderChart()}
    </Box>
  );
};

// Resource usage chart component
export const ResourceUsageChart: React.FC<{ timeRange: string }> = ({ timeRange }) => {
  const theme = useTheme();
  const timeSeriesData = generateTimeSeriesData(timeRange, 'resources');

  const data = {
    labels: timeSeriesData.labels,
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: Array.from({ length: timeSeriesData.labels.length }, () => 
          Math.floor(Math.random() * 40) + 40
        ),
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        borderColor: 'rgba(33, 150, 243, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        yAxisID: 'percentage',
      },
      {
        label: 'Memory Usage (%)',
        data: Array.from({ length: timeSeriesData.labels.length }, () => 
          Math.floor(Math.random() * 30) + 50
        ),
        backgroundColor: 'rgba(156, 39, 176, 0.1)',
        borderColor: 'rgba(156, 39, 176, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        yAxisID: 'percentage',
      },
      {
        label: 'Storage Usage (GB)',
        data: Array.from({ length: timeSeriesData.labels.length }, () => 
          Math.floor(Math.random() * 200) + 800
        ),
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        borderColor: 'rgba(255, 152, 0, 1)',
        borderWidth: 2,
        fill: false,
        tension: 0.3,
        yAxisID: 'storage',
        hidden: true, // Hidden by default
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: theme.palette.text.primary,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: theme.palette.background.paper,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.secondary,
        borderColor: theme.palette.divider,
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            if (label.includes('Storage')) {
              return `${label}: ${value} GB`;
            }
            return `${label}: ${value}%`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: theme.palette.divider,
        },
        ticks: {
          color: theme.palette.text.secondary,
        },
      },
      percentage: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        min: 0,
        max: 100,
        grid: {
          color: theme.palette.divider,
        },
        ticks: {
          color: theme.palette.text.secondary,
          callback: function(value: any) {
            return value + '%';
          },
        },
      },
      storage: {
        type: 'linear' as const,
        display: false,
        position: 'right' as const,
        min: 0,
        max: 1200,
        ticks: {
          color: theme.palette.text.secondary,
          callback: function(value: any) {
            return value + ' GB';
          },
        },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  return (
    <Box sx={{ height: 300, position: 'relative' }}>
      <Line data={data} options={options} />
    </Box>
  );
};