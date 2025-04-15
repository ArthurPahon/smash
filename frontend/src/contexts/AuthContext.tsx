import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService, User } from '../services/auth';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isLoggedIn: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (
    name: string,
    email: string,
    password: string,
    country?: string,
    state?: string
  ) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const checkAuth = async () => {
    try {
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
      } else {
        setUser(null);
      }
    } catch (err) {
      setUser(null);
      setError("Erreur lors de la vérification de l'authentification");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
    const interval = setInterval(checkAuth, 30000);
    return () => clearInterval(interval);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authService.login({ email, password });
      setUser(response.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la connexion');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    navigate('/login');
  };

  const register = async (
    name: string,
    email: string,
    password: string,
    country?: string,
    state?: string
  ) => {
    try {
      setLoading(true);
      setError(null);
      await authService.register({ name, email, password, country, state });
      navigate('/login', {
        state: { message: 'Inscription réussie ! Vous pouvez maintenant vous connecter.' },
      });
    } catch (err: any) {
      setError(err.response?.data?.message || "Erreur lors de l'inscription");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        isLoggedIn: !!user,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth doit être utilisé à l'intérieur d'un AuthProvider");
  }
  return context;
};
