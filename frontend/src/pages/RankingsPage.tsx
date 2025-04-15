import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  CircularProgress,
  Avatar,
} from '@mui/material';
import { getGlobalRankings } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface Ranking {
  user: {
    id: number;
    name: string;
    profile_picture: string | null;
  };
  tournaments_participated: number;
  average_rank: number | null;
}

const RankingsPage: React.FC = () => {
  const { user } = useAuth();
  const [rankings, setRankings] = useState<Ranking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  const fetchRankings = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await getGlobalRankings({
        page: page + 1,
        per_page: rowsPerPage,
      });
      setRankings(response.rankings);
      setTotalCount(response.total);
    } catch (err) {
      setError('Erreur lors du chargement des classements');
      console.error('Erreur lors du chargement des classements:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankings();
  }, [page, rowsPerPage]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <Typography color="error">{error}</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 4 }}>
        Classement Global
      </Typography>

      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rang</TableCell>
                <TableCell>Joueur</TableCell>
                <TableCell align="right">Tournois participés</TableCell>
                <TableCell align="right">Classement moyen</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rankings.map((ranking, index) => (
                <TableRow
                  key={ranking.user.id}
                  sx={{
                    backgroundColor:
                      user?.id === ranking.user.id ? 'rgba(255, 0, 0, 0.1)' : 'inherit',
                  }}
                >
                  <TableCell component="th" scope="row">
                    {page * rowsPerPage + index + 1}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar
                        src={ranking.user.profile_picture || undefined}
                        alt={ranking.user.name}
                      >
                        {ranking.user.name[0]}
                      </Avatar>
                      <Typography>{ranking.user.name}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">{ranking.tournaments_participated}</TableCell>
                  <TableCell align="right">
                    {ranking.average_rank ? ranking.average_rank.toFixed(1) : '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Lignes par page"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} sur ${count}`}
        />
      </Paper>
    </Container>
  );
};

export default RankingsPage;
