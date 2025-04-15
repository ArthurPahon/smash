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
  Grid,
  Card,
  CardContent,
  Divider,
  Stack,
} from '@mui/material';
import { CalendarToday, People, EmojiEvents, Gavel } from '@mui/icons-material';

interface TournamentResponse {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  registration_deadline: string | null;
  max_participants: number;
  current_participants: number;
  status: string;
  format: string;
  rules: string;
  prize_pool: string;
  created_at: string;
  updated_at: string;
  organizer: {
    id: number;
    name: string;
  };
  registrations?: Array<{
    id: number;
    user_id: number;
    tournament_id: number;
    registration_date: string;
    status: string;
    seed?: number;
    user?: {
      id: number;
      username: string;
    };
  }>;
}

interface Tournament extends Omit<TournamentResponse, 'registration_deadline'> {
  registration_deadline: string;
}

const statusColors = {
  upcoming: 'info',
  ongoing: 'success',
  completed: 'warning',
  cancelled: 'error',
} as const;

const statusLabels = {
  upcoming: 'À venir',
  ongoing: 'En cours',
  completed: 'Terminé',
  cancelled: 'Annulé',
} as const;

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
  const [isRegistering, setIsRegistering] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [registrationError, setRegistrationError] = useState('');

  useEffect(() => {
    const fetchTournament = async () => {
      try {
        setLoading(true);
        setError('');
        const tournamentId = Number(id);
        if (isNaN(tournamentId)) {
          setError('ID de tournoi invalide');
          setLoading(false);
          return;
        }
        const response = await getTournament(tournamentId);
        const data = response as unknown as Tournament;
        setTournament(data);
        if (
          user &&
          data.registrations?.some((reg: { user_id: number }) => reg.user_id === user.id)
        ) {
          setIsRegistered(true);
        }
      } catch (err) {
        setError('Échec du chargement du tournoi');
        console.error('Erreur lors du chargement du tournoi:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTournament();
  }, [id, user]);

  const handleRegisterClick = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setShowConfirmDialog(true);
  };

  const handleRegister = async () => {
    if (!user || !tournament) return;

    try {
      setIsRegistering(true);
      setRegistrationError('');

      if (tournament.status !== 'upcoming') {
        setRegistrationError('Les inscriptions sont fermées pour ce tournoi');
        return;
      }

      if (new Date(tournament.registration_deadline) <= new Date()) {
        setRegistrationError("La date limite d'inscription est dépassée");
        return;
      }

      if (tournament.current_participants >= tournament.max_participants) {
        setRegistrationError('Le tournoi est complet');
        return;
      }

      await registerForTournament(tournament.id);
      setTournament(prev =>
        prev ? { ...prev, current_participants: prev.current_participants + 1 } : null
      );
      setIsRegistered(true);
      setShowConfirmDialog(false);
    } catch (err: any) {
      setRegistrationError(err.response?.data?.error || "Échec de l'inscription au tournoi");
      console.error("Erreur lors de l'inscription:", err);
    } finally {
      setIsRegistering(false);
    }
  };

  const handleUnregister = async () => {
    if (!user || !tournament) return;

    try {
      setIsRegistering(true);
      setRegistrationError('');
      await unregisterFromTournament(tournament.id);
      setTournament(prev =>
        prev ? { ...prev, current_participants: prev.current_participants - 1 } : null
      );
      setIsRegistered(false);
    } catch (err: any) {
      setRegistrationError(err.response?.data?.error || 'Échec du désengagement du tournoi');
      console.error('Erreur lors du désengagement:', err);
    } finally {
      setIsRegistering(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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
        <Alert severity="error">Tournoi non trouvé</Alert>
      </Container>
    );
  }

  const isRegistrationOpen = new Date(tournament.registration_deadline) > new Date();
  const isFull = tournament.current_participants >= tournament.max_participants;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {registrationError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {registrationError}
        </Alert>
      )}

      <Paper sx={{ p: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {tournament.name}
            </Typography>
            <Stack direction="row" spacing={2} alignItems="center">
              <Chip
                label={statusLabels[tournament.status as keyof typeof statusLabels]}
                color={statusColors[tournament.status as keyof typeof statusColors]}
              />
              <Typography variant="body2" color="textSecondary">
                Organisé par {tournament.organizer.name}
              </Typography>
            </Stack>
          </Box>

          <Box>
            {isRegistered ? (
              <Button
                variant="outlined"
                color="error"
                onClick={handleUnregister}
                disabled={isRegistering || tournament.status !== 'upcoming'}
              >
                {isRegistering ? 'Désinscription...' : 'Se désinscrire'}
              </Button>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleRegisterClick}
                disabled={
                  isRegistering ||
                  tournament.status !== 'upcoming' ||
                  new Date(tournament.registration_deadline) <= new Date() ||
                  tournament.current_participants >= tournament.max_participants
                }
              >
                {isRegistering
                  ? 'Inscription...'
                  : tournament.current_participants >= tournament.max_participants
                    ? 'Tournoi complet'
                    : new Date(tournament.registration_deadline) <= new Date()
                      ? 'Inscriptions fermées'
                      : tournament.status !== 'upcoming'
                        ? 'Tournoi non disponible'
                        : "S'inscrire"}
              </Button>
            )}
          </Box>
        </Box>

        <Box sx={{ display: 'grid', gridTemplateColumns: { md: '2fr 1fr' }, gap: 4 }}>
          <Card sx={{ mb: { xs: 3, md: 0 } }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Description
              </Typography>
              <Typography variant="body1" paragraph>
                {tournament.description}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Rules
              </Typography>
              <Typography variant="body1">{tournament.rules}</Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Stack spacing={3}>
                <Box>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    <CalendarToday sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Dates
                  </Typography>
                  <Typography variant="body2">
                    Début: {formatDate(tournament.start_date)}
                  </Typography>
                  <Typography variant="body2">Fin: {formatDate(tournament.end_date)}</Typography>
                  <Typography variant="body2">
                    Registration deadline: {formatDate(tournament.registration_deadline)}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    <People sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Participants
                  </Typography>
                  <Typography variant="body2">
                    {tournament.current_participants} / {tournament.max_participants}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    <EmojiEvents sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Prize pool
                  </Typography>
                  <Typography variant="body2">{tournament.prize_pool}€</Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    <Gavel sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Format
                  </Typography>
                  <Typography variant="body2">
                    {tournament.format === 'simple_elimination'
                      ? 'Simple élimination'
                      : tournament.format}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      </Paper>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Participants inscrits</h2>
        {tournament.registrations && tournament.registrations.length > 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {tournament.registrations.map(registration => (
                <li key={registration.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <span className="inline-flex items-center justify-center h-10 w-10 rounded-full bg-gray-500">
                          <span className="text-lg font-medium leading-none text-white">
                            {registration.user?.username?.[0]?.toUpperCase() || '?'}
                          </span>
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {registration.user?.username || 'Utilisateur inconnu'}
                        </div>
                        <div className="text-sm text-gray-500">
                          Inscrit le {new Date(registration.registration_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      {registration.seed && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Tête de série #{registration.seed}
                        </span>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-center py-8 bg-white shadow sm:rounded-lg">
            <p className="text-gray-500">Aucun participant inscrit pour le moment.</p>
          </div>
        )}
      </div>

      <Dialog open={showConfirmDialog} onClose={() => setShowConfirmDialog(false)}>
        <DialogTitle>Confirmer l'inscription</DialogTitle>
        <DialogContent>
          <Typography>
            Voulez-vous vraiment vous inscrire au tournoi "{tournament?.name}" ?
          </Typography>
          {tournament && (
            <>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                Date de début : {formatDate(tournament.start_date)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Format : {tournament.format}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Places : {tournament.current_participants}/{tournament.max_participants}
              </Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDialog(false)}>Annuler</Button>
          <Button onClick={handleRegister} color="primary" disabled={isRegistering}>
            {isRegistering ? 'Inscription...' : 'Confirmer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TournamentDetailPage;
