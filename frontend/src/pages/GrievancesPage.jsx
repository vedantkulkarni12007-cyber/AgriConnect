// =============================================================
// Grievances Page
// File and track disputes/issues
// =============================================================

import { useState, useEffect } from 'react';
import { AlertTriangle, Plus, Clock } from 'lucide-react';
import { getGrievances, createGrievance } from '../services/api';
import { StatusBadge } from '../components/Badges';
import { LoadingState } from '../components/States';

const ISSUE_TYPES = [
  'Price Dispute',
  'Quality Dispute',
  'Payment Delay',
  'Delivery Issue',
  'Fraud',
  'Other',
];

export default function GrievancesPage() {
  const [grievances, setGrievances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ transaction_id: '', issue_type: '', description: '' });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => { loadGrievances(); }, []);

  async function loadGrievances() {
    setLoading(true);
    const res = await getGrievances();
    if (res.success) setGrievances(res.data);
    setLoading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!formData.issue_type || !formData.description) return;
    setSubmitting(true);
    const res = await createGrievance(formData);
    if (res.success) {
      setGrievances(prev => [{ ...res.data, issue_type: formData.issue_type, description: formData.description, status: 'open' }, ...prev]);
      setShowForm(false);
      setFormData({ transaction_id: '', issue_type: '', description: '' });
      setSubmitted(true);
    }
    setSubmitting(false);
  }

  const statusLabel = { open: 'Open', under_review: 'Under Review', resolved: 'Resolved' };
  const statusColor = { open: 'badge-yellow', under_review: 'badge-blue', resolved: 'badge-green' };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Grievances</h1>
          <p className="text-gray-500 text-sm mt-1">File and track disputes transparently</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          File Grievance
        </button>
      </div>

      {/* Success message */}
      {submitted && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-xl text-sm">
          ✓ Your grievance has been filed. Our team will review it within 2-3 business days.
        </div>
      )}

      {/* Filing form */}
      {showForm && (
        <div className="card border-2 border-amber-200">
          <h2 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            File a New Grievance
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Transaction ID (optional)</label>
              <input
                className="input"
                placeholder="e.g. txn001 — leave blank if not related"
                value={formData.transaction_id}
                onChange={(e) => setFormData(p => ({ ...p, transaction_id: e.target.value }))}
              />
            </div>
            <div>
              <label className="label">Issue Type *</label>
              <select
                className="input"
                value={formData.issue_type}
                onChange={(e) => setFormData(p => ({ ...p, issue_type: e.target.value }))}
                required
              >
                <option value="">Select issue type</option>
                {ISSUE_TYPES.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Describe the Issue *</label>
              <textarea
                className="input resize-none"
                rows={4}
                placeholder="Describe what happened in detail. Include dates, amounts, and names where relevant."
                value={formData.description}
                onChange={(e) => setFormData(p => ({ ...p, description: e.target.value }))}
                required
              />
            </div>
            <div className="flex gap-3">
              <button type="submit" disabled={submitting} className="btn-primary disabled:opacity-60">
                {submitting ? 'Submitting...' : 'Submit Grievance'}
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* List */}
      {loading ? <LoadingState /> : (
        <div className="space-y-4">
          {grievances.length === 0 ? (
            <div className="card text-center py-12">
              <AlertTriangle className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 font-medium">No grievances filed</p>
              <p className="text-sm text-gray-400 mt-1">Use the button above to file a dispute.</p>
            </div>
          ) : grievances.map(g => (
            <div key={g.id} className="card">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className={statusColor[g.status] || 'badge-gray'}>
                      {statusLabel[g.status] || g.status}
                    </span>
                    <span className="badge-gray">{g.issue_type}</span>
                    {g.transaction_id && (
                      <span className="text-xs text-gray-400 font-mono">#{g.transaction_id}</span>
                    )}
                  </div>
                  <p className="text-gray-700 text-sm mt-2 leading-relaxed">{g.description}</p>
                  {g.resolution && (
                    <div className="mt-3 bg-green-50 border border-green-100 rounded-lg px-3 py-2">
                      <p className="text-xs font-semibold text-green-700 mb-0.5">Resolution:</p>
                      <p className="text-sm text-green-800">{g.resolution}</p>
                    </div>
                  )}
                  <div className="flex items-center gap-1 text-xs text-gray-400 mt-2">
                    <Clock className="w-3.5 h-3.5" />
                    Filed {g.created_at ? new Date(g.created_at).toLocaleDateString('en-IN') : 'recently'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
