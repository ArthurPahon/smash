import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isLoggedIn, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-smash-red">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Link to="/" className="text-white font-bold text-xl">
                Smash Tournois
              </Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link
                  to="/tournaments"
                  className="text-white hover:bg-smash-red-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Tournois
                </Link>
                <Link
                  to="/rankings"
                  className="text-white hover:bg-smash-red-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                >
                  Classements
                </Link>
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6">
              {isLoggedIn ? (
                <>
                  <Link
                    to="/profile"
                    className="text-white hover:bg-smash-red-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Profil
                  </Link>
                  <button
                    className="ml-2 text-white hover:bg-smash-red-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                    onClick={handleLogout}
                  >
                    Déconnexion
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-white hover:bg-smash-red-800 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Connexion
                  </Link>
                  <Link
                    to="/register"
                    className="ml-2 bg-white text-smash-red hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Inscription
                  </Link>
                </>
              )}
            </div>
          </div>
          <div className="-mr-2 flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="bg-smash-red inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-smash-red-800 focus:outline-none"
            >
              <span className="sr-only">Ouvrir le menu</span>
              {isOpen ? (
                <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Menu mobile */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link
              to="/tournaments"
              className="text-white hover:bg-smash-red-800 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
            >
              Tournois
            </Link>
            <Link
              to="/rankings"
              className="text-white hover:bg-smash-red-800 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
            >
              Classements
            </Link>
            {isLoggedIn ? (
              <>
                <Link
                  to="/profile"
                  className="text-white hover:bg-smash-red-800 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                >
                  Profil
                </Link>
                <button
                  className="text-white hover:bg-smash-red-800 hover:text-white block w-full text-left px-3 py-2 rounded-md text-base font-medium"
                  onClick={handleLogout}
                >
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-white hover:bg-smash-red-800 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                >
                  Connexion
                </Link>
                <Link
                  to="/register"
                  className="text-white hover:bg-smash-red-800 hover:text-white block px-3 py-2 rounded-md text-base font-medium"
                >
                  Inscription
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
