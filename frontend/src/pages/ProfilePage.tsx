import React from 'react';

const ProfilePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Profil utilisateur</h1>

        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <div className="flex items-center space-x-4 mb-6">
            <div className="h-20 w-20 rounded-full bg-blue-600 flex items-center justify-center text-white text-2xl font-bold">
              U
            </div>
            <div>
              <h2 className="text-xl font-bold">Utilisateur</h2>
              <p className="text-gray-600">utilisateur@example.com</p>
              <p className="text-sm text-gray-500">Membre depuis: Janvier 2023</p>
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="font-semibold text-lg mb-3">Informations personnelles</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Nom</p>
                <p>Utilisateur Test</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Nom d'utilisateur</p>
                <p>user123</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p>utilisateur@example.com</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Téléphone</p>
                <p>Non spécifié</p>
              </div>
            </div>

            <div className="mt-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                Modifier le profil
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6">
          <h3 className="font-semibold text-lg mb-3">Statistiques</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-blue-600">0</p>
              <p className="text-gray-600">Tournois participés</p>
            </div>
            <div className="border rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-green-600">0</p>
              <p className="text-gray-600">Victoires</p>
            </div>
            <div className="border rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-purple-600">0</p>
              <p className="text-gray-600">Classement ELO</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
