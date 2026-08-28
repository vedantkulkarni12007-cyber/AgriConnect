// =============================================================
// Register Page
// =============================================================

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const ROLES = [
  { value: 'farmer', label: 'Farmer', emoji: '🌾', desc: 'I grow crops and want to sell at better prices' },
  { value: 'buyer',  label: 'Buyer',  emoji: '🏪', desc: 'I want to buy produce directly from farmers' },
  { value: 'fpo',    label: 'FPO / Farmer Group', emoji: '🤝', desc: 'I represent a group of farmers' },
];

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '', email: '', phone: '', password: '', role: '', location: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.role) { setError('Please select your role.'); return; }
    setLoading(true);
    setError('');
    const result = await register(formData);
    setLoading(false);
    if (result.success) {
      if (formData.role === 'farmer') navigate('/farmer/dashboard');
      else if (formData.role === 'buyer') navigate('/buyer/dashboard');
      else navigate('/fpo/dashboard');
    } else {
      setError(result.message);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 bg-green-800 rounded-xl flex items-center justify-center">
              <Sprout className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-green-900">KrishiLink</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-500 text-sm mt-1">Join KrishiLink to access better prices and buyers</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Role Selection */}
            <div>
              <label className="label">I am a *</label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {ROLES.map(r => (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => handleChange('role', r.value)}
                    className={`flex flex-col items-center p-4 rounded-xl border-2 transition-all text-center ${
                      formData.role === r.value
                        ? 'border-green-600 bg-green-50'
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                  >
                    <span className="text-2xl mb-1">{r.emoji}</span>
                    <span className="font-semibold text-sm text-gray-800">{r.label}</span>
                    <span className="text-xs text-gray-500 mt-1 leading-tight">{r.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="label">Full Name *</label>
                <input className="input" placeholder="Ramesh Patil" value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)} required />
              </div>
              <div>
                <label className="label">Phone Number *</label>
                <input className="input" placeholder="9876543210" type="tel" value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)} required />
              </div>
              <div>
                <label className="label">Email</label>
                <input className="input" placeholder="name@email.com" type="email" value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)} />
              </div>
              <div className="sm:col-span-2">
                <label className="label">Location (Village / District) *</label>
                <input className="input" placeholder="Lasalgaon, Nashik" value={formData.location}
                  onChange={(e) => handleChange('location', e.target.value)} required />
              </div>
              <div className="sm:col-span-2">
                <label className="label">Password *</label>
                <input className="input" type="password" placeholder="Choose a secure password" value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)} required minLength={6} />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-xl">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-60">
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-green-700 font-semibold hover:underline">Login</Link>
          </p>
        </div>

        <p className="text-center text-xs text-gray-400 mt-4">
          Demo mode: Registration creates a local account. Connect Supabase for real auth.
        </p>
      </div>
    </div>
  );
}
