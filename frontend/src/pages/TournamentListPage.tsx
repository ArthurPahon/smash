import React from 'react';

const TournamentListPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Liste des tournois</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <p>Chargement des tournois...</p>
      </div>
    </div>
  );
};

export default TournamentListPage;
