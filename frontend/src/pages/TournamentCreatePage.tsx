import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTournament } from '../services/api';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  SelectChangeEvent,
  Card,
  CardContent,
  Stack,
  Divider,
} from '@mui/material';
import { EmojiEvents, Gavel, People, CalendarToday, LocationOn } from '@mui/icons-material';

interface TournamentFormData {
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  registration_deadline: string;
  max_participants: number;
  format: string;
  game: string;
  rules: string;
  prize_pool: string;
  address: string;
}

const initialFormData: TournamentFormData = {
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  registration_deadline: '',
  max_participants: 16,
  format: 'single_elimination',
  game: 'Super Smash Bros. Ultimate',
  rules: '',
  prize_pool: '',
  address: '',
};

const formatOptions = [
  { value: 'single_elimination', label: 'Simple Elimination' },
  { value: 'double_elimination', label: 'Double Elimination' },
  { value: 'round_robin', label: 'Round Robin' },
  { value: 'swiss', label: 'Swiss System' },
];

const gameOptions = [
  'Super Smash Bros. Ultimate',
  'Super Smash Bros. Melee',
  'Super Smash Bros. Brawl',
  'Super Smash Bros. for Wii U',
  'Super Smash Bros. for 3DS',
];

const TournamentCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<TournamentFormData>(initialFormData);
  const [error, setError] = useState<string | null>('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validation des champs requis
      if (!formData.name || !formData.start_date || !formData.end_date) {
        setError('Veuillez remplir tous les champs obligatoires');
        setLoading(false);
        return;
      }

      // Validation des dates
      const startDate = new Date(formData.start_date);
      const endDate = new Date(formData.end_date);
      const now = new Date();

      if (startDate < now) {
        setError('La date de début doit être dans le futur');
        setLoading(false);
        return;
      }

      if (endDate <= startDate) {
        setError('La date de fin doit être après la date de début');
        setLoading(false);
        return;
      }

      // Convertir les dates au format ISO sans le 'Z' à la fin
      const formattedData = {
        ...formData,
        start_date: startDate.toISOString().slice(0, -1),
        end_date: endDate.toISOString().slice(0, -1),
        registration_deadline: formData.registration_deadline
          ? new Date(formData.registration_deadline).toISOString().slice(0, -1)
          : undefined,
      };

      await createTournament(formattedData);
      navigate('/tournaments');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as any).response;
        if (response?.data?.error) {
          setError(response.data.error);
        } else {
          setError('Une erreur est survenue lors de la création du tournoi');
        }
      } else {
        setError('Une erreur est survenue');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange =
    (field: keyof TournamentFormData) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent) => {
      const value = e.target.value;
      setFormData(prev => ({
        ...prev,
        [field]: field === 'max_participants' ? Number(value) : value,
      }));
    };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 4 }}>
        Créer un nouveau tournoi
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 4, borderRadius: 2 }}>
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Stack spacing={4}>
            <Card>
              <CardContent>
                <Stack spacing={3}>
                  <Box>
                    <TextField
                      required
                      fullWidth
                      label="Nom du tournoi"
                      value={formData.name}
                      onChange={handleChange('name')}
                      variant="outlined"
                    />
                  </Box>

                  <Box>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Description"
                      value={formData.description}
                      onChange={handleChange('description')}
                      variant="outlined"
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Stack spacing={3}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CalendarToday /> Dates et participants
                  </Typography>
                  <Divider />
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <TextField
                        required
                        fullWidth
                        type="date"
                        label="Date de début"
                        value={formData.start_date}
                        onChange={handleChange('start_date')}
                        InputLabelProps={{ shrink: true }}
                        variant="outlined"
                      />
                    </Box>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <TextField
                        required
                        fullWidth
                        type="date"
                        label="Date de fin"
                        value={formData.end_date}
                        onChange={handleChange('end_date')}
                        InputLabelProps={{ shrink: true }}
                        variant="outlined"
                      />
                    </Box>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <TextField
                        fullWidth
                        type="date"
                        label="Date limite d'inscription"
                        value={formData.registration_deadline}
                        onChange={handleChange('registration_deadline')}
                        InputLabelProps={{ shrink: true }}
                        variant="outlined"
                      />
                    </Box>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <TextField
                        required
                        fullWidth
                        type="number"
                        label="Nombre maximum de participants"
                        value={formData.max_participants}
                        onChange={handleChange('max_participants')}
                        variant="outlined"
                        inputProps={{ min: 2, max: 128 }}
                      />
                    </Box>
                  </Box>
                </Stack>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Stack spacing={3}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Gavel /> Format et règles
                  </Typography>
                  <Divider />
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <FormControl fullWidth>
                        <InputLabel>Format du tournoi</InputLabel>
                        <Select
                          value={formData.format}
                          onChange={handleChange('format')}
                          label="Format du tournoi"
                          variant="outlined"
                        >
                          {formatOptions.map(option => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Box>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <FormControl fullWidth>
                        <InputLabel>Jeu</InputLabel>
                        <Select
                          value={formData.game}
                          onChange={handleChange('game')}
                          label="Jeu"
                          variant="outlined"
                        >
                          {gameOptions.map(option => (
                            <MenuItem key={option} value={option}>
                              {option}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Box>
                  </Box>
                  <Box>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Règles du tournoi"
                      value={formData.rules}
                      onChange={handleChange('rules')}
                      variant="outlined"
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Stack spacing={3}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <EmojiEvents /> Prix et lieu
                  </Typography>
                  <Divider />
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <TextField
                        fullWidth
                        label="Fonds de prix"
                        value={formData.prize_pool}
                        onChange={handleChange('prize_pool')}
                        variant="outlined"
                        placeholder="Ex: 1000$"
                      />
                    </Box>
                    <Box sx={{ flex: '1 1 300px' }}>
                      <TextField
                        fullWidth
                        label="Adresse"
                        value={formData.address}
                        onChange={handleChange('address')}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </Stack>
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button
                onClick={() => navigate('/tournaments')}
                variant="outlined"
                color="primary"
                size="large"
              >
                Annuler
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
                size="large"
              >
                {loading ? 'Création en cours...' : 'Créer le tournoi'}
              </Button>
            </Box>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
};

export default TournamentCreatePage;
