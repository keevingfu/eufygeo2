import React, { useState, useEffect } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import * as echarts from 'echarts';

// Example of keyword dashboard with pyramid visualization
// This demonstrates:
// 1. ECharts integration for pyramid chart
// 2. Material-UI DataGrid for keyword table
// 3. Real-time filtering and search
// 4. Bulk operations UI

interface Keyword {
  id: number;
  keyword: string;
  search_volume: number;
  priority_tier: string;
  aio_status: 'active' | 'inactive' | 'monitoring';
}

const KeywordDashboard: React.FC = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  
  // Pyramid chart configuration
  const pyramidOption = {
    series: [{
      type: 'funnel',
      sort: 'ascending',
      data: [
        { value: 8, name: 'P0: Core (>30K)' },
        { value: 17, name: 'P1: High (20-30K)' },
        { value: 45, name: 'P2: Medium (15-20K)' },
        { value: 120, name: 'P3: Low (10-15K)' },
        { value: 660, name: 'P4: Long-tail (<10K)' }
      ]
    }]
  };

  const columns: GridColDef[] = [
    { field: 'keyword', headerName: 'Keyword', flex: 2 },
    { field: 'search_volume', headerName: 'Volume', width: 120 },
    { field: 'priority_tier', headerName: 'Tier', width: 80 },
    { field: 'aio_status', headerName: 'AIO Status', width: 120 }
  ];

  return (
    <div>
      <div id="pyramid-chart" style={{ width: '100%', height: '400px' }} />
      <DataGrid rows={keywords} columns={columns} />
    </div>
  );
};