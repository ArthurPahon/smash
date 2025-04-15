import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  getTournament,
  updateTournament,
  registerForTournament,
  unregisterFromTournament,
} from '../services/api';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Chip,
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
  current_participants: number;
  status: string;
  format: string;
  game: string;
  rules: string;
  prizes: string;
  address: string;
  organizer: {
    id: number;
    username: string;
    name: string;
  };
}

interface TournamentResponse {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  registration_deadline: string | null;
  max_participants: number;
  participants_count: number;
  current_participants: number;
  status: string;
  format: string;
  game: string;
  rules: string;
  prizes: string;
  address: string;
  organizer: {
    id: number;
    username: string;
    name: string;
  };
}

const statusOptions = [
  { value: 'preparation', label: 'Preparation' },
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'finished', label: 'Finished' },
  { value: 'cancelled', label: 'Cancelled' },
];

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

const TournamentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState<Partial<Tournament>>({});

  const fetchTournament = async () => {
    try {
      setLoading(true);
      setError('');
      const data = (await getTournament(Number(id))) as TournamentResponse;
      const tournamentData: Tournament = {
        id: data.id,
        name: data.name,
        description: data.description,
        start_date: data.start_date,
        end_date: data.end_date,
        registration_deadline: data.registration_deadline || null,
        max_participants: data.max_participants,
        participants_count: data.participants_count || 0,
        current_participants: data.current_participants || 0,
        status: data.status,
        format: data.format,
        game: data.game || '',
        rules: data.rules || '',
        prizes: data.prizes || '',
        address: data.address,
        organizer: {
          id: data.organizer.id,
          username: data.organizer.username || '',
          name: data.organizer.name || data.organizer.username || '',
        },
      };
      setTournament(tournamentData);
    } catch (err) {
      setError('Failed to load tournament details');
      console.error('Error fetching tournament:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTournament();
  }, [id]);

  const handleEdit = () => {
    if (tournament) {
      setEditData({
        name: tournament.name,
        description: tournament.description,
        start_date: tournament.start_date.split('T')[0],
        end_date: tournament.end_date.split('T')[0],
        registration_deadline: tournament.registration_deadline?.split('T')[0],
        max_participants: tournament.max_participants,
        status: tournament.status,
        format: tournament.format,
        game: tournament.game,
        rules: tournament.rules,
        prizes: tournament.prizes,
        address: tournament.address,
      });
      setEditMode(true);
    }
  };

  const handleSave = async () => {
    try {
      setError('');
      const updateData = {
        ...editData,
        registration_deadline: editData.registration_deadline || undefined,
      };
      await updateTournament(Number(id), updateData);
      await fetchTournament();
      setEditMode(false);
    } catch (err) {
      setError('Failed to update tournament');
      console.error('Error updating tournament:', err);
    }
  };

  const handleRegister = async () => {
    try {
      setError('');
      await registerForTournament(Number(id));
      await fetchTournament();
    } catch (err) {
      setError('Failed to register for tournament');
      console.error('Error registering for tournament:', err);
    }
  };

  const handleUnregister = async () => {
    try {
      setError('');
      await unregisterFromTournament(Number(id));
      await fetchTournament();
    } catch (err) {
      setError('Failed to unregister from tournament');
      console.error('Error unregistering from tournament:', err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleChange =
    (field: keyof Tournament) =>
    (
      event: React.ChangeEvent<HTMLInputElement | { value: unknown }> | SelectChangeEvent<string>
    ) => {
      setEditData(prev => ({
        ...prev,
        [field]: event.target.value,
      }));
    };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!tournament) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">Tournament not found</Alert>
      </Container>
    );
  }

  const isOrganizer = user?.id === tournament.organizer.id;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          {tournament.name}
        </Typography>
        <Box>
          {isOrganizer && !editMode && (
            <Button variant="contained" color="primary" onClick={handleEdit}>
              Edit Tournament
            </Button>
          )}
          {user && !isOrganizer && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleRegister}
              disabled={tournament.participants_count >= tournament.max_participants}
            >
              Register
            </Button>
          )}
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        <Box sx={{ flex: '1 1 60%', minWidth: '300px' }}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography>{tournament.description}</Typography>
          </Paper>
        </Box>

        <Box sx={{ flex: '1 1 35%', minWidth: '300px' }}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Tournament Details
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Status
                </Typography>
                <Chip
                  label={tournament.status}
                  color={getStatusColor(tournament.status)}
                  sx={{ mt: 0.5 }}
                />
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Format
                </Typography>
                <Typography>{tournament.format}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Game
                </Typography>
                <Typography>{tournament.game}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Participants
                </Typography>
                <Typography>
                  {tournament.current_participants} / {tournament.max_participants}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Organizer
                </Typography>
                <Typography>{tournament.organizer.name}</Typography>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>

      {editMode ? (
        <Paper sx={{ p: 3 }}>
          <Box component="form" noValidate sx={{ mt: 1 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <TextField
                  fullWidth
                  label="Name"
                  value={editData.name}
                  onChange={handleChange('name')}
                />
              </Box>
              <Box>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Description"
                  value={editData.description}
                  onChange={handleChange('description')}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Box sx={{ flex: '1 1 300px' }}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Start Date"
                    value={editData.start_date}
                    onChange={handleChange('start_date')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <TextField
                    fullWidth
                    type="date"
                    label="End Date"
                    value={editData.end_date}
                    onChange={handleChange('end_date')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Box sx={{ flex: '1 1 300px' }}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Registration Deadline"
                    value={editData.registration_deadline}
                    onChange={handleChange('registration_deadline')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Participants"
                    value={editData.max_participants}
                    onChange={handleChange('max_participants')}
                  />
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Box sx={{ flex: '1 1 300px' }}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={editData.status}
                      onChange={handleChange('status')}
                      label="Status"
                    >
                      <MenuItem value="upcoming">Upcoming</MenuItem>
                      <MenuItem value="ongoing">Ongoing</MenuItem>
                      <MenuItem value="completed">Completed</MenuItem>
                      <MenuItem value="cancelled">Cancelled</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <TextField
                    fullWidth
                    label="Format"
                    value={editData.format}
                    onChange={handleChange('format')}
                  />
                </Box>
              </Box>
              <Box>
                <TextField
                  fullWidth
                  label="Game"
                  value={editData.game}
                  onChange={handleChange('game')}
                />
              </Box>
              <Box>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Rules"
                  value={editData.rules}
                  onChange={handleChange('rules')}
                />
              </Box>
              <Box>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Prizes"
                  value={editData.prizes}
                  onChange={handleChange('prizes')}
                />
              </Box>
              <Box>
                <TextField
                  fullWidth
                  label="Address"
                  value={editData.address}
                  onChange={handleChange('address')}
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button onClick={() => setEditMode(false)}>Cancel</Button>
                <Button type="submit" variant="contained" color="primary" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </Box>
          </Box>
        </Paper>
      ) : null}
    </Container>
  );
};

export default TournamentDetailPage;
