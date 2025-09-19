import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Grid,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  Tooltip,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridToolbar,
} from '@mui/x-data-grid';
import {
  Upload as UploadIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Visibility as VisibilityIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as AIIcon,
} from '@mui/icons-material';
import * as echarts from 'echarts';
import axios from 'axios';

interface Keyword {
  id: number;
  keyword: string;
  search_volume: number;
  difficulty: number;
  cpc: number;
  priority_tier: string;
  aio_status: string;
  current_rank: number;
  traffic: number;
  content_count: number;
  avg_position_30d: number;
  clicks_30d: number;
}

interface FilterState {
  priority_tier: string;
  aio_status: string;
  product_category: string;
  min_volume: number | '';
  max_volume: number | '';
}

const KeywordDashboard: React.FC = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    priority_tier: '',
    aio_status: '',
    product_category: '',
    min_volume: '',
    max_volume: '',
  });
  const [pyramidData, setPyramidData] = useState<any>(null);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

  // Fetch keywords
  const fetchKeywords = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });

      const response = await axios.get(`${API_BASE_URL}/keywords?${params}`);
      setKeywords(response.data.keywords);
    } catch (error) {
      console.error('Error fetching keywords:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Fetch pyramid data
  const fetchPyramidData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/keywords/pyramid`);
      setPyramidData(response.data);
      renderPyramidChart(response.data);
    } catch (error) {
      console.error('Error fetching pyramid data:', error);
    }
  };

  // Render pyramid chart
  const renderPyramidChart = (data: any) => {
    const chartDom = document.getElementById('pyramid-chart');
    if (!chartDom) return;

    const myChart = echarts.init(chartDom);
    const option = {
      title: {
        text: 'Keyword Priority Pyramid',
        left: 'center',
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const tier = params.data;
          return `${params.name}<br/>
            Keywords: ${tier.value}<br/>
            Avg Volume: ${Math.round(tier.avg_volume).toLocaleString()}<br/>
            AIO Active: ${tier.aio_active_count}`;
        },
      },
      series: [
        {
          name: 'Keywords',
          type: 'funnel',
          left: '10%',
          top: 60,
          bottom: 60,
          width: '80%',
          min: 0,
          max: Math.max(...data.tiers.map((t: any) => parseInt(t.count))),
          minSize: '0%',
          maxSize: '100%',
          sort: 'ascending',
          gap: 2,
          label: {
            show: true,
            position: 'inside',
            formatter: '{b}: {c} keywords',
          },
          labelLine: {
            length: 10,
            lineStyle: {
              width: 1,
              type: 'solid',
            },
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1,
          },
          emphasis: {
            label: {
              fontSize: 20,
            },
          },
          data: data.tiers.map((tier: any) => ({
            value: parseInt(tier.count),
            name: tier.priority_tier,
            avg_volume: tier.avg_volume,
            aio_active_count: tier.aio_active_count,
            itemStyle: {
              color: {
                'P0': '#ff4444',
                'P1': '#ff8c00',
                'P2': '#ffd700',
                'P3': '#32cd32',
                'P4': '#87ceeb',
              }[tier.priority_tier],
            },
          })),
        },
      ],
    };

    myChart.setOption(option);
  };

  useEffect(() => {
    fetchKeywords();
    fetchPyramidData();
  }, [fetchKeywords]);

  // Handle file upload
  const handleFileUpload = async () => {
    if (!uploadFile) return;

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      setUploadProgress(10);
      const response = await axios.post(
        `${API_BASE_URL}/keywords/bulk-import`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total!
            );
            setUploadProgress(progress);
          },
        }
      );

      if (response.data.success) {
        alert(`Successfully imported ${response.data.imported} keywords`);
        setUploadDialogOpen(false);
        fetchKeywords();
        fetchPyramidData();
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed');
    } finally {
      setUploadProgress(0);
      setUploadFile(null);
    }
  };

  // Export keywords
  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });

      const response = await axios.get(
        `${API_BASE_URL}/keywords/export?${params}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `keywords-export-${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  // Auto-classify keywords
  const handleAutoClassify = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/keywords/classify`);
      if (response.data.success) {
        alert(`Classified ${response.data.classified} keywords`);
        fetchKeywords();
        fetchPyramidData();
      }
    } catch (error) {
      console.error('Classification error:', error);
    }
  };

  // Column definitions
  const columns: GridColDef[] = [
    {
      field: 'keyword',
      headerName: 'Keyword',
      flex: 2,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {params.value}
          </Typography>
          <Box sx={{ mt: 0.5 }}>
            {params.row.content_count > 0 && (
              <Chip
                size="small"
                label={`${params.row.content_count} content`}
                color="primary"
                variant="outlined"
                sx={{ mr: 0.5 }}
              />
            )}
            {params.row.aio_status === 'active' && (
              <Chip
                size="small"
                icon={<AIIcon />}
                label="AIO Active"
                color="success"
                sx={{ mr: 0.5 }}
              />
            )}
          </Box>
        </Box>
      ),
    },
    {
      field: 'priority_tier',
      headerName: 'Tier',
      width: 80,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          sx={{
            backgroundColor: {
              'P0': '#ff4444',
              'P1': '#ff8c00',
              'P2': '#ffd700',
              'P3': '#32cd32',
              'P4': '#87ceeb',
            }[params.value as string],
            color: 'white',
            fontWeight: 'bold',
          }}
        />
      ),
    },
    {
      field: 'search_volume',
      headerName: 'Volume',
      width: 120,
      type: 'number',
      valueFormatter: (params) => params.value?.toLocaleString() || '0',
    },
    {
      field: 'difficulty',
      headerName: 'Difficulty',
      width: 100,
      type: 'number',
      renderCell: (params: GridRenderCellParams) => (
        <LinearProgress
          variant="determinate"
          value={params.value || 0}
          sx={{
            width: '100%',
            height: 8,
            borderRadius: 4,
            backgroundColor: '#e0e0e0',
            '& .MuiLinearProgress-bar': {
              backgroundColor:
                params.value > 70
                  ? '#ff4444'
                  : params.value > 40
                  ? '#ff8c00'
                  : '#32cd32',
            },
          }}
        />
      ),
    },
    {
      field: 'current_rank',
      headerName: 'Rank',
      width: 80,
      type: 'number',
      renderCell: (params: GridRenderCellParams) => {
        if (!params.value || params.value > 100) return '-';
        const change = params.row.previous_rank
          ? params.row.previous_rank - params.value
          : 0;
        return (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2">{params.value}</Typography>
            {change !== 0 && (
              <Typography
                variant="caption"
                sx={{
                  ml: 0.5,
                  color: change > 0 ? 'success.main' : 'error.main',
                }}
              >
                {change > 0 ? '↑' : '↓'}{Math.abs(change)}
              </Typography>
            )}
          </Box>
        );
      },
    },
    {
      field: 'clicks_30d',
      headerName: '30d Clicks',
      width: 100,
      type: 'number',
      valueFormatter: (params) => params.value?.toLocaleString() || '0',
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title="View Details">
            <IconButton size="small">
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="View Trend">
            <IconButton size="small">
              <TrendingUpIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h4" fontWeight="bold">
          Keyword Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => {
              fetchKeywords();
              fetchPyramidData();
            }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
          >
            Export
          </Button>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Import CSV
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Keywords
              </Typography>
              <Typography variant="h4">
                {pyramidData?.summary.total_keywords || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                AIO Coverage
              </Typography>
              <Typography variant="h4">
                {pyramidData?.summary.aio_coverage || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Traffic
              </Typography>
              <Typography variant="h4">
                {pyramidData?.summary.total_traffic?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography color="textSecondary" gutterBottom>
                  Auto-Classify
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={handleAutoClassify}
                >
                  Run
                </Button>
              </Box>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Classify unassigned keywords
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Left Side - Pyramid Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '600px' }}>
            <Box id="pyramid-chart" sx={{ width: '100%', height: '100%' }} />
          </Paper>
        </Grid>

        {/* Right Side - Data Grid */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '600px' }}>
            {/* Filters */}
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Tier</InputLabel>
                <Select
                  value={filters.priority_tier}
                  label="Tier"
                  onChange={(e) =>
                    setFilters({ ...filters, priority_tier: e.target.value })
                  }
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="P0">P0</MenuItem>
                  <MenuItem value="P1">P1</MenuItem>
                  <MenuItem value="P2">P2</MenuItem>
                  <MenuItem value="P3">P3</MenuItem>
                  <MenuItem value="P4">P4</MenuItem>
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>AIO Status</InputLabel>
                <Select
                  value={filters.aio_status}
                  label="AIO Status"
                  onChange={(e) =>
                    setFilters({ ...filters, aio_status: e.target.value })
                  }
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="monitoring">Monitoring</MenuItem>
                </Select>
              </FormControl>

              <TextField
                size="small"
                label="Min Volume"
                type="number"
                value={filters.min_volume}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    min_volume: e.target.value ? parseInt(e.target.value) : '',
                  })
                }
                sx={{ width: 120 }}
              />

              <TextField
                size="small"
                label="Max Volume"
                type="number"
                value={filters.max_volume}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    max_volume: e.target.value ? parseInt(e.target.value) : '',
                  })
                }
                sx={{ width: 120 }}
              />
            </Box>

            {/* Data Grid */}
            <DataGrid
              rows={keywords}
              columns={columns}
              loading={loading}
              checkboxSelection
              disableRowSelectionOnClick
              onRowSelectionModelChange={(newSelection) => {
                setSelectedRows(newSelection as number[]);
              }}
              components={{
                Toolbar: GridToolbar,
              }}
              sx={{ height: 'calc(100% - 60px)' }}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Import Keywords from CSV</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              CSV should contain columns: keyword, search_volume, difficulty,
              cpc, category, intent
            </Alert>

            <input
              type="file"
              accept=".csv"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              style={{ marginBottom: 16 }}
            />

            {uploadProgress > 0 && (
              <LinearProgress
                variant="determinate"
                value={uploadProgress}
                sx={{ mb: 2 }}
              />
            )}

            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button onClick={() => setUploadDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                variant="contained"
                onClick={handleFileUpload}
                disabled={!uploadFile}
              >
                Upload
              </Button>
            </Box>
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default KeywordDashboard;