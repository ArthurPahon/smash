import axios from 'axios';
import { authService } from './auth';

const API_URL = 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_URL,
});

// Fonction de test ping-pong
export const ping = async () => {
  try {
    console.log('=== ENVOI PING ===');
    const response = await api.get('/tournaments/ping');
    console.log('Réponse reçue:', response.data);
    return response.data;
  } catch (error) {
    console.error('Erreur lors du ping:', error);
    throw error;
  }
};

// Intercepteur pour ajouter le token JWT aux requêtes
api.interceptors.request.use(
  config => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const userData = JSON.parse(userStr);
      if (userData.access_token) {
        config.headers.Authorization = `Bearer ${userData.access_token}`;
      }
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs de réponse
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      authService.logout();
      // Au lieu d'utiliser history, on va simplement supprimer le token
      // La redirection sera gérée par le composant qui utilise l'API
    }
    return Promise.reject(error);
  }
);

export const getTournaments = async (params: {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.per_page) queryParams.append('per_page', params.per_page.toString());
    if (params.search) queryParams.append('search', params.search);
    if (params.status && params.status !== 'all') queryParams.append('status', params.status);

    const response = await api.get(`/tournaments?${queryParams.toString()}`);

    // Convertir les données du backend vers le format frontend
    return {
      tournaments: response.data.tournaments.map((t: any) => ({
        id: t.id,
        name: t.name,
        description: t.description,
        start_date: t.start_date,
        end_date: t.end_date,
        registration_deadline: t.registration_deadline,
        max_participants: t.max_participants,
        current_participants: t.current_participants,
        status: t.status,
        format: t.format,
        game: t.game,
        rules: t.rules,
        prize_pool: t.prize_pool,
        address: t.address,
        created_at: t.created_at,
        updated_at: t.updated_at,
        organizer: t.organizer,
      })),
      total: response.data.total,
      pages: response.data.pages,
      current_page: response.data.current_page,
    };
  } catch (error) {
    console.error('Erreur lors de la récupération des tournois:', error);
    throw error;
  }
};

export const getTournament = async (id: number) => {
  try {
    const response = await api.get(`/tournaments/${id}`);

    // Convertir les données du backend vers le format frontend
    const t = response.data;
    return {
      id: t.id,
      name: t.name,
      description: t.description,
      start_date: t.start_date,
      end_date: t.end_date,
      registration_deadline: t.registration_deadline,
      max_participants: t.max_participants,
      current_participants: t.current_participants,
      status: t.status,
      format: t.format,
      game: t.game,
      rules: t.rules,
      prize_pool: t.prize_pool,
      address: t.address,
      created_at: t.created_at,
      updated_at: t.updated_at,
      organizer: t.organizer,
      registrations: t.registrations || [],
    };
  } catch (error) {
    console.error('Erreur lors de la récupération du tournoi:', error);
    throw error;
  }
};

export const createTournament = async (data: {
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  registration_deadline?: string;
  max_participants?: number;
  format?: string;
  game?: string;
  rules?: string;
  prizes?: string;
  address?: string;
}) => {
  try {
    const response = await api.post('/tournaments', data);
    return response.data;
  } catch (error) {
    console.error('Error creating tournament:', error);
    throw error;
  }
};

export const updateTournament = async (
  id: number,
  data: {
    name?: string;
    description?: string;
    start_date?: string;
    end_date?: string;
    registration_deadline?: string;
    max_participants?: number;
    status?: string;
    format?: string;
    game?: string;
    rules?: string;
    prizes?: string;
    address?: string;
  }
) => {
  try {
    const response = await api.put(`/tournaments/${id}`, data);
    return response.data;
  } catch (error) {
    console.error('Error updating tournament:', error);
    throw error;
  }
};

export const deleteTournament = async (id: number) => {
  try {
    const response = await api.delete(`/tournaments/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting tournament:', error);
    throw error;
  }
};

export const registerForTournament = async (tournamentId: number) => {
  try {
    const response = await api.post(`/tournaments/${tournamentId}/register`);
    return response.data;
  } catch (error) {
    console.error('Error registering for tournament:', error);
    throw error;
  }
};

export const unregisterFromTournament = async (tournamentId: number) => {
  try {
    const response = await api.post(`/tournaments/${tournamentId}/unregister`);
    return response.data;
  } catch (error) {
    console.error('Error unregistering from tournament:', error);
    throw error;
  }
};

export const getTournamentBrackets = async (tournamentId: number) => {
  const response = await api.get(`/tournaments/${tournamentId}/brackets`);
  return response.data;
};

export const updateMatchResult = async (
  tournamentId: number,
  matchId: number,
  data: {
    winner_id?: number;
    score?: string;
    status?: string;
  }
) => {
  const response = await api.patch(`/tournaments/${tournamentId}/matches/${matchId}`, data);
  return response.data;
};

// Rankings
export const getGlobalRankings = async (params?: { page?: number; per_page?: number }) => {
  try {
    const response = await api.get('/rankings', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching global rankings:', error);
    throw error;
  }
};

export const getTournamentRankings = async (tournamentId: number) => {
  try {
    const response = await api.get(`/rankings/tournaments/${tournamentId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching tournament rankings:', error);
    throw error;
  }
};

export const getUserRankings = async (userId: number) => {
  try {
    const response = await api.get(`/rankings/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user rankings:', error);
    throw error;
  }
};

export default api;
