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
  Chip,
  Paper,
} from '@mui/material';

interface Tournament {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  registration_deadline: string;
  max_participants: number;
  current_participants: number;
  status: string;
  format: string;
  game: string;
  rules: string;
  prize_pool: string;
  address: string;
  created_at: string;
  updated_at: string;
  organizer: {
    id: number;
    name: string;
  };
}

const statusOptions = [
  { value: 'all', label: 'Tous' },
  { value: 'upcoming', label: 'À venir' },
  { value: 'ongoing', label: 'En cours' },
  { value: 'completed', label: 'Terminé' },
  { value: 'cancelled', label: 'Annulé' },
];

const TournamentListPage: React.FC = () => {
  const { user } = useAuth();
  const [allTournaments, setAllTournaments] = useState<Tournament[]>([]);
  const [filteredTournaments, setFilteredTournaments] = useState<Tournament[]>([]);
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
        per_page: 100,
        status: filterStatus === 'all' ? '' : filterStatus,
      });
      setAllTournaments(response.tournaments);
      setTotalPages(response.pages);
      setTotalItems(response.total);
    } catch (err) {
      setError('Échec du chargement des tournois');
      console.error('Erreur lors du chargement des tournois:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTournaments();
  }, [page, filterStatus]);

  useEffect(() => {
    const filtered = allTournaments.filter(tournament => {
      const matchesSearch =
        tournament.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tournament.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = filterStatus === 'all' || tournament.status === filterStatus;
      return matchesSearch && matchesStatus;
    });
    setFilteredTournaments(filtered);
  }, [allTournaments, searchTerm, filterStatus]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleStatusChange = (event: SelectChangeEvent) => {
    setFilterStatus(event.target.value);
  };

  const handlePageChange = (_: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'upcoming':
        return 'info';
      case 'ongoing':
        return 'success';
      case 'completed':
        return 'warning';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
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
          Tournois
        </Typography>
        {user && (
          <Button component={Link} to="/tournaments/create" variant="contained" color="primary">
            Créer un tournoi
          </Button>
        )}
      </Box>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Box sx={{ flex: '1 1 300px' }}>
            <TextField
              fullWidth
              label="Rechercher des tournois"
              value={searchTerm}
              onChange={handleSearch}
              placeholder="Nom du tournoi..."
            />
          </Box>
          <Box sx={{ flex: '1 1 300px' }}>
            <FormControl fullWidth>
              <InputLabel>Statut</InputLabel>
              <Select value={filterStatus} onChange={handleStatusChange} label="Statut">
                {statusOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
          gap: 3,
        }}
      >
        {filteredTournaments.map(tournament => (
          <Card
            key={tournament.id}
            sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}
          >
            <CardContent sx={{ flexGrow: 1 }}>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {tournament.name}
                </Typography>
                <Chip
                  label={
                    statusOptions.find(opt => opt.value === tournament.status)?.label ||
                    tournament.status
                  }
                  color={getStatusColor(tournament.status)}
                  size="small"
                />
              </Box>
              <Typography color="textSecondary" gutterBottom>
                Organisé par {tournament.organizer.name}
              </Typography>
              <Typography variant="body2" paragraph>
                {tournament.description?.slice(0, 100)}
                {tournament.description?.length > 100 ? '...' : ''}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Début: {formatDate(tournament.start_date)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Fin: {formatDate(tournament.end_date)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Date limite d'inscription:{' '}
                  {tournament.registration_deadline
                    ? formatDate(tournament.registration_deadline)
                    : 'Non spécifiée'}
                </Typography>
              </Box>
              <Box
                sx={{
                  mt: 2,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Typography variant="body2">
                  Participants: {tournament.current_participants} /{' '}
                  {tournament.max_participants || '∞'}
                </Typography>
                {tournament.prize_pool && (
                  <Typography variant="body2" color="primary">
                    Prix: {tournament.prize_pool}€
                  </Typography>
                )}
              </Box>
            </CardContent>
            <CardActions>
              <Button
                component={Link}
                to={`/tournaments/${tournament.id}`}
                size="small"
                color="primary"
                fullWidth
              >
                Voir les détails
              </Button>
            </CardActions>
          </Card>
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
