import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:justify-between">
          <div className="mb-6 md:mb-0">
            <Link to="/" className="text-xl font-bold">
              Smash Tournois
            </Link>
            <p className="mt-2 text-sm text-gray-400">
              La plateforme de gestion de tournois Super Smash Bros.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider">Plateforme</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link to="/tournaments" className="text-gray-400 hover:text-white">
                    Tournois
                  </Link>
                </li>
                <li>
                  <Link to="/rankings" className="text-gray-400 hover:text-white">
                    Classements
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider">Légal</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link to="/privacy" className="text-gray-400 hover:text-white">
                    Confidentialité
                  </Link>
                </li>
                <li>
                  <Link to="/terms" className="text-gray-400 hover:text-white">
                    Conditions d'utilisation
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider">Contact</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a
                    href="mailto:contact@smashtournois.com"
                    className="text-gray-400 hover:text-white"
                  >
                    Email
                  </a>
                </li>
                <li>
                  <a
                    href="https://twitter.com/smashtournois"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-white"
                  >
                    Twitter
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-700 pt-8 md:flex md:items-center md:justify-between">
          <p className="text-sm text-gray-400">
            &copy; {new Date().getFullYear()} Smash Tournois. Tous droits réservés.
          </p>
          <div className="mt-4 md:mt-0">
            <p className="text-sm text-gray-400">
              Super Smash Bros. est une marque déposée de Nintendo. Ce site n'est pas affilié à
              Nintendo.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
