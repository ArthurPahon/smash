import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const HomePage: React.FC = () => {
  const { isLoggedIn } = useAuth();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-smash-red text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-4">
              Smash Tournois
            </h1>
            <p className="text-xl md:text-2xl mb-8">
              La plateforme de gestion de tournois Super Smash Bros.
            </p>
            {!isLoggedIn ? (
              <div className="flex justify-center space-x-4">
                <Link
                  to="/register"
                  className="bg-white text-smash-red hover:bg-gray-100 px-6 py-3 rounded-lg font-medium text-lg transition duration-200"
                >
                  S'inscrire
                </Link>
                <Link
                  to="/login"
                  className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-smash-red px-6 py-3 rounded-lg font-medium text-lg transition duration-200"
                >
                  Se connecter
                </Link>
              </div>
            ) : (
              <Link
                to="/tournaments"
                className="inline-block bg-white text-smash-red hover:bg-gray-100 px-6 py-3 rounded-lg font-medium text-lg transition duration-200"
              >
                Voir les tournois
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Fonctionnalités</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Tournois */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-smash-red mb-4">
                <svg
                  className="h-12 w-12"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Tournois</h3>
              <p className="text-gray-600">
                Créez et gérez des tournois, suivez les matchs en direct et découvrez les résultats.
              </p>
            </div>

            {/* Classements */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-smash-red mb-4">
                <svg
                  className="h-12 w-12"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Classements</h3>
              <p className="text-gray-600">
                Consultez les classements des joueurs et suivez votre progression dans le classement
                ELO.
              </p>
            </div>

            {/* Profil */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="text-smash-red mb-4">
                <svg
                  className="h-12 w-12"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Profil</h3>
              <p className="text-gray-600">
                Gérez votre profil, consultez vos statistiques et suivez votre historique de
                tournois.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Prêt à rejoindre la communauté ?</h2>
          <p className="text-xl mb-8">
            Inscrivez-vous maintenant et commencez à participer aux tournois !
          </p>
          {!isLoggedIn ? (
            <Link
              to="/register"
              className="inline-block bg-smash-red hover:bg-red-700 px-6 py-3 rounded-lg font-medium text-lg transition duration-200"
            >
              Créer un compte
            </Link>
          ) : (
            <Link
              to="/tournaments"
              className="inline-block bg-smash-red hover:bg-red-700 px-6 py-3 rounded-lg font-medium text-lg transition duration-200"
            >
              Voir les tournois
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
