// =============================================================
// Authentication Context
// Manages the logged-in user state throughout the app
// 
// DEMO MODE: clicking "Continue as Farmer/Buyer/FPO" sets a fake user
// LIVE MODE: will use Supabase Auth (integration point prepared)
// =============================================================

import { createContext, useContext, useState, useEffect } from 'react';
import { DEMO_USERS } from '../data/demoData';

// Create the context (this is how React shares data between components)
const AuthContext = createContext(null);

// AuthProvider wraps the whole app and provides user state everywhere
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app start, check if a user was saved in localStorage
  // (so they stay logged in when they refresh the page)
  useEffect(() => {
    const savedUser = localStorage.getItem('krishilink_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('krishilink_user');
      }
    }
    setLoading(false);
  }, []);

  // Demo login: immediately logs in with pre-defined demo user
  // No password or API needed
  const demoLogin = (role) => {
    const demoUser = DEMO_USERS[role];
    if (demoUser) {
      setUser(demoUser);
      localStorage.setItem('krishilink_user', JSON.stringify(demoUser));
    }
  };

  // Real login (future Supabase integration)
  // For now: checks against demo users by email
  const login = async (email, password) => {
    // TODO: Replace with Supabase Auth
    // const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    
    // Demo fallback: find demo user by email
    const demoUser = Object.values(DEMO_USERS).find(u => u.email === email);
    if (demoUser) {
      setUser(demoUser);
      localStorage.setItem('krishilink_user', JSON.stringify(demoUser));
      return { success: true };
    }
    return { success: false, message: 'Invalid credentials. Use demo login below.' };
  };

  // Real register (future Supabase integration)
  const register = async (userData) => {
    // TODO: Replace with Supabase Auth
    // const { data, error } = await supabase.auth.signUp({ email, password });
    
    // Demo: just log them in with a mock user
    const mockUser = {
      id: `user-${Date.now()}`,
      name: userData.name,
      role: userData.role,
      location: userData.location || 'Maharashtra',
      email: userData.email,
      phone: userData.phone,
    };
    setUser(mockUser);
    localStorage.setItem('krishilink_user', JSON.stringify(mockUser));
    return { success: true };
  };

  // Logout
  const logout = () => {
    setUser(null);
    localStorage.removeItem('krishilink_user');
  };

  const value = {
    user,
    loading,
    isLoggedIn: !!user,
    isFarmer: user?.role === 'farmer',
    isBuyer: user?.role === 'buyer',
    isFPO: user?.role === 'fpo',
    login,
    register,
    demoLogin,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context in any component
// Usage: const { user, logout } = useAuth();
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
