import React from 'react';
import { useParams } from 'react-router-dom';

const TournamentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Détails du tournoi {id}</h1>
      <div className="bg-white shadow-md rounded-lg p-6">
        <p>Chargement des détails du tournoi...</p>
      </div>
    </div>
  );
};

export default TournamentDetailPage;
