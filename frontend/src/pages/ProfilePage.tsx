import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Profil utilisateur</h1>

        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          {/* En-tête du profil */}
          <div className="bg-smash-red p-6">
            <div className="flex items-center space-x-4">
              <div className="h-24 w-24 rounded-full bg-white flex items-center justify-center text-smash-red text-3xl font-bold border-4 border-white shadow-lg">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="text-white">
                <h2 className="text-2xl font-bold">{user?.name}</h2>
                <p className="text-sm opacity-90">{user?.email}</p>
                <p className="text-sm opacity-80">
                  Membre depuis:{' '}
                  {new Date(user?.registration_date || '').toLocaleDateString('fr-FR', {
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
              </div>
            </div>
          </div>

          {/* Informations personnelles */}
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Informations personnelles</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Nom d'utilisateur</p>
                <p className="font-medium text-gray-800">{user?.name}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Email</p>
                <p className="font-medium text-gray-800">{user?.email}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Pays</p>
                <p className="font-medium text-gray-800">{user?.country || 'Non spécifié'}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Région</p>
                <p className="font-medium text-gray-800">{user?.state || 'Non spécifiée'}</p>
              </div>
            </div>

            <div className="mt-6">
              <button className="px-6 py-2 bg-smash-red text-white rounded-lg hover:bg-smash-red-800 transition duration-200 flex items-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                  />
                </svg>
                <span>Modifier le profil</span>
              </button>
            </div>
          </div>

          {/* Statistiques */}
          <div className="border-t border-gray-200 p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Statistiques</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-smash-red to-red-600 rounded-lg p-6 text-white shadow-lg">
                <p className="text-4xl font-bold">0</p>
                <p className="text-sm opacity-90">Tournois participés</p>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-lg">
                <p className="text-4xl font-bold">0</p>
                <p className="text-sm opacity-90">Victoires</p>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
                <p className="text-4xl font-bold">1000</p>
                <p className="text-sm opacity-90">Classement ELO</p>
              </div>
            </div>
          </div>

          {/* Historique des tournois */}
          <div className="border-t border-gray-200 p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-800">Historique des tournois</h3>
            <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
              Aucun tournoi participé pour le moment
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
