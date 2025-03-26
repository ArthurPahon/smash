import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <h1 className="text-9xl font-extrabold text-blue-600">404</h1>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Page non trouvée</h2>
          <p className="mt-2 text-sm text-gray-600">
            La page que vous recherchez n'existe pas ou a été déplacée.
          </p>
        </div>
        <div>
          <Link
            to="/"
            className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Retour à l'accueil
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
