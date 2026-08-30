// =============================================================
// Grievances & Customer Support Page
// File and track support tickets & transaction disputes
// =============================================================

import { useState, useEffect } from 'react';
import { AlertTriangle, Plus, Clock, CheckCircle2, MessageSquare, ShieldAlert } from 'lucide-react';
import { getGrievances, createGrievance } from '../services/api';
import { LoadingState } from '../components/States';

const CATEGORIES = [
  'Price Dispute',
  'Quality Dispute',
  'Payment Delay',
  'Delivery & Transport',
  'Listing Accuracy',
  'Account & Profile',
  'General Inquiry',
];

export default function GrievancesPage() {
  const [grievances, setGrievances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    transaction_id: '',
    category: 'Price Dispute',
    reason: '',
    description: '',
    priority: 'MEDIUM'
  });
  const [submitting, setSubmitting] = useState(false);
  const [submittedMessage, setSubmittedMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const loadGrievances = async () => {
    setLoading(true);
    setErrorMessage(null);
    const res = await getGrievances();
    if (res && res.success && Array.isArray(res.data)) {
      setGrievances(res.data);
    } else if (res && !res.success) {
      setErrorMessage(res.error || 'Failed to load support tickets. Please refresh.');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadGrievances();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!formData.reason || !formData.description) return;
    setSubmitting(true);
    setErrorMessage(null);

    const payload = {
      category: formData.category,
      reason: formData.reason,
      description: formData.description,
      priority: formData.priority,
      transaction_id: formData.transaction_id || null,
    };

    const res = await createGrievance(payload);
    if (res && res.success) {
      const createdItem = res.data || {
        id: `tkt-${Date.now()}`,
        ticket_number: `KL-TKT-${Date.now().toString().slice(-6)}`,
        reason: `[${formData.category}] ${formData.reason}`,
        description: formData.description,
        status: 'OPEN',
        created_at: new Date().toISOString()
      };
      setGrievances(prev => [createdItem, ...prev]);
      setShowForm(false);
      setFormData({ transaction_id: '', category: 'Price Dispute', reason: '', description: '', priority: 'MEDIUM' });
      setSubmittedMessage('Your ticket has been submitted. Support will investigate and update you within 24 hours.');
      setTimeout(() => setSubmittedMessage(null), 8000);
    } else {
      setErrorMessage(res?.error || 'Could not submit support ticket. Please check fields and retry.');
    }
    setSubmitting(false);
  }

  const getStatusBadge = (status = 'OPEN') => {
    const s = status.toUpperCase();
    if (s === 'OPEN') return 'bg-amber-100 text-amber-800 border border-amber-200';
    if (s === 'UNDER_REVIEW' || s === 'IN_PROGRESS') return 'bg-blue-100 text-blue-800 border border-blue-200';
    if (s === 'RESOLVED' || s === 'CLOSED') return 'bg-green-100 text-green-800 border border-green-200';
    if (s === 'REJECTED') return 'bg-red-100 text-red-800 border border-red-200';
    return 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support & Grievances</h1>
          <p className="text-gray-500 text-sm mt-1">Raise complaints, report listing/delivery issues, or request transaction arbitration.</p>
        </div>
        <button
          onClick={() => { setShowForm(!showForm); setErrorMessage(null); }}
          className="btn-primary flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          {showForm ? 'Close Form' : 'New Ticket'}
        </button>
      </div>

      {/* Success alert */}
      {submittedMessage && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3.5 rounded-xl text-sm flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
          <span>{submittedMessage}</span>
        </div>
      )}

      {/* Error alert */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3.5 rounded-xl text-sm flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 text-red-600 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Ticket creation form */}
      {showForm && (
        <div className="card border-2 border-green-200 shadow-md">
          <h2 className="font-bold text-gray-900 mb-4 flex items-center gap-2 text-lg">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            File a Support Ticket / Dispute
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label">Category *</label>
                <select
                  className="input"
                  value={formData.category}
                  onChange={(e) => setFormData(p => ({ ...p, category: e.target.value }))}
                  required
                >
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Priority</label>
                <select
                  className="input"
                  value={formData.priority}
                  onChange={(e) => setFormData(p => ({ ...p, priority: e.target.value }))}
                >
                  <option value="LOW">Low — Question or Minor</option>
                  <option value="MEDIUM">Medium — General Issue</option>
                  <option value="HIGH">High — Quality or Delay</option>
                  <option value="URGENT">Urgent — Payment Dispute</option>
                </select>
              </div>
            </div>

            <div>
              <label className="label">Subject / Summary *</label>
              <input
                className="input"
                placeholder="Brief summary of the issue (e.g. Quality did not match Grade A specification)"
                value={formData.reason}
                onChange={(e) => setFormData(p => ({ ...p, reason: e.target.value }))}
                required
                minLength={3}
                maxLength={150}
              />
            </div>

            <div>
              <label className="label">Transaction / Order ID (optional)</label>
              <input
                className="input"
                placeholder="e.g. 5e179e22-046c-49f5 — leave empty if not related to an order"
                value={formData.transaction_id}
                onChange={(e) => setFormData(p => ({ ...p, transaction_id: e.target.value }))}
              />
            </div>

            <div>
              <label className="label">Detailed Description *</label>
              <textarea
                className="input resize-none"
                rows={4}
                placeholder="Provide specific details including weights, timestamps, and communications so our operations team can resolve promptly."
                value={formData.description}
                onChange={(e) => setFormData(p => ({ ...p, description: e.target.value }))}
                required
                minLength={10}
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button type="submit" disabled={submitting} className="btn-primary disabled:opacity-60">
                {submitting ? 'Submitting...' : 'Submit Support Ticket'}
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tickets List */}
      {loading ? <LoadingState message="Loading your tickets..." /> : (
        <div className="space-y-4">
          {grievances.length === 0 ? (
            <div className="card text-center py-12">
              <MessageSquare className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-700 font-semibold">No active support tickets</p>
              <p className="text-sm text-gray-400 mt-1">If you experience any issues with produce, payments, or logistics, click 'New Ticket' above.</p>
            </div>
          ) : (
            grievances.map(g => (
              <div key={g.id} className="card hover:border-gray-300 transition-all">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1.5">
                      <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${getStatusBadge(g.status)}`}>
                        {g.status || 'OPEN'}
                      </span>
                      {g.ticket_number && (
                        <span className="text-xs font-mono bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-medium">
                          {g.ticket_number}
                        </span>
                      )}
                      {g.transaction_id && (
                        <span className="text-xs text-gray-400 font-mono">
                          Order: #{g.transaction_id.slice(0, 8)}
                        </span>
                      )}
                    </div>
                    <h3 className="font-bold text-gray-900 text-base mt-1">{g.reason}</h3>
                    <p className="text-gray-700 text-sm mt-1.5 leading-relaxed">{g.description}</p>
                    
                    {g.resolution && (
                      <div className="mt-3 bg-green-50 border border-green-200 rounded-xl px-4 py-3">
                        <p className="text-xs font-bold text-green-800 mb-0.5">Official Resolution:</p>
                        <p className="text-sm text-green-900">{g.resolution}</p>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-1.5 text-xs text-gray-400 mt-3">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Filed on {g.created_at ? new Date(g.created_at).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }) : 'recently'}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
