import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getTournaments } from '../services/api';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
  CircularProgress,
  Alert,
  SelectChangeEvent,
} from '@mui/material';

interface Tournament {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  registration_deadline: string | null;
  max_participants: number;
  participants_count: number;
  status: string;
  format: string;
  game: string;
  rules: string;
  prizes: string;
  address: string;
  organizer: {
    id: number;
    username: string;
  };
}

const statusOptions = [
  { value: 'all', label: 'All' },
  { value: 'preparation', label: 'Preparation' },
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'finished', label: 'Finished' },
  { value: 'cancelled', label: 'Cancelled' },
];

const TournamentListPage: React.FC = () => {
  const { user } = useAuth();
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchTournaments = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await getTournaments({
        page,
        per_page: 10,
        search: searchTerm,
        status: filterStatus,
      });
      setTournaments(response.tournaments);
      setTotalPages(response.pages);
      setTotalItems(response.total);
    } catch (err) {
      setError('Failed to load tournaments');
      console.error('Error fetching tournaments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTournaments();
  }, [page, searchTerm, filterStatus]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handleStatusChange = (event: SelectChangeEvent) => {
    setFilterStatus(event.target.value);
    setPage(1);
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'preparation':
        return 'info';
      case 'ongoing':
        return 'success';
      case 'finished':
        return 'warning';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          Tournaments
        </Typography>
        {user && (
          <Button component={Link} to="/tournaments/create" variant="contained" color="primary">
            Create Tournament
          </Button>
        )}
      </Box>

      <Box mb={4}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Box sx={{ flex: '1 1 300px' }}>
            <TextField
              fullWidth
              label="Search tournaments"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSearch(e)}
            />
          </Box>
          <Box sx={{ flex: '1 1 300px' }}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select value={filterStatus} onChange={handleStatusChange} label="Status">
                {statusOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {tournaments.map(tournament => (
          <Box key={tournament.id} sx={{ flex: '1 1 300px', maxWidth: '100%' }}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" gutterBottom>
                  {tournament.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Organized by {tournament.organizer.username}
                </Typography>
                <Typography variant="body2" paragraph>
                  {tournament.description?.slice(0, 100)}
                  {tournament.description?.length > 100 ? '...' : ''}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Start: {formatDate(tournament.start_date)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  End: {formatDate(tournament.end_date)}
                </Typography>
                <Typography variant="body2">
                  Participants: {tournament.participants_count} /{' '}
                  {tournament.max_participants || '∞'}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  component={Link}
                  to={`/tournaments/${tournament.id}`}
                  size="small"
                  color="primary"
                >
                  View Details
                </Button>
              </CardActions>
            </Card>
          </Box>
        ))}
      </Box>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <Pagination count={totalPages} page={page} onChange={handlePageChange} color="primary" />
        </Box>
      )}
    </Container>
  );
};

export default TournamentListPage;
