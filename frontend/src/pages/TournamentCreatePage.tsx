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
} from '@mui/material';

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
  prizes: string;
  address: string;
}

const initialFormData: TournamentFormData = {
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  registration_deadline: '',
  max_participants: 0,
  format: '',
  game: '',
  rules: '',
  prizes: '',
  address: '',
};

const formatOptions = [
  { value: 'single_elimination', label: 'Single Elimination' },
  { value: 'double_elimination', label: 'Double Elimination' },
  { value: 'round_robin', label: 'Round Robin' },
  { value: 'swiss', label: 'Swiss System' },
];

const TournamentCreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<TournamentFormData>(initialFormData);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await createTournament(formData);
      navigate(`/tournaments/${response.id}`);
    } catch (err) {
      setError('Failed to create tournament');
      console.error('Error creating tournament:', err);
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
      <Typography variant="h4" component="h1" gutterBottom>
        Create Tournament
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Box>
              <TextField
                required
                fullWidth
                label="Tournament Name"
                value={formData.name}
                onChange={handleChange('name')}
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
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Box sx={{ flex: '1 1 300px' }}>
                <TextField
                  required
                  fullWidth
                  type="date"
                  label="Start Date"
                  value={formData.start_date}
                  onChange={handleChange('start_date')}
                  InputLabelProps={{ shrink: true }}
                />
              </Box>
              <Box sx={{ flex: '1 1 300px' }}>
                <TextField
                  required
                  fullWidth
                  type="date"
                  label="End Date"
                  value={formData.end_date}
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
                  value={formData.registration_deadline}
                  onChange={handleChange('registration_deadline')}
                  InputLabelProps={{ shrink: true }}
                />
              </Box>
              <Box sx={{ flex: '1 1 300px' }}>
                <TextField
                  fullWidth
                  type="number"
                  label="Max Participants"
                  value={formData.max_participants}
                  onChange={handleChange('max_participants')}
                />
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Box sx={{ flex: '1 1 300px' }}>
                <FormControl fullWidth>
                  <InputLabel>Format</InputLabel>
                  <Select value={formData.format} onChange={handleChange('format')} label="Format">
                    {formatOptions.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              <Box sx={{ flex: '1 1 300px' }}>
                <TextField
                  fullWidth
                  label="Game"
                  value={formData.game}
                  onChange={handleChange('game')}
                />
              </Box>
            </Box>

            <Box>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Rules"
                value={formData.rules}
                onChange={handleChange('rules')}
              />
            </Box>

            <Box>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Prizes"
                value={formData.prizes}
                onChange={handleChange('prizes')}
              />
            </Box>

            <Box>
              <TextField
                fullWidth
                label="Address"
                value={formData.address}
                onChange={handleChange('address')}
              />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button onClick={() => navigate('/tournaments')}>Cancel</Button>
              <Button type="submit" variant="contained" color="primary" disabled={loading}>
                {loading ? 'Creating...' : 'Create Tournament'}
              </Button>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default TournamentCreatePage;
