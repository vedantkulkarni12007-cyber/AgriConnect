// =============================================================
// Offers Page
// Farmers & Buyers see and manage negotiations
// =============================================================

import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { IndianRupee, CheckCircle2, XCircle, Eye, Clock } from 'lucide-react';
import { getOffers, acceptOffer, rejectOffer } from '../services/api';
import { StatusBadge } from '../components/Badges';
import { LoadingState, EmptyState } from '../components/States';

export default function OffersPage() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [updatingId, setUpdatingId] = useState(null);
  const [error, setError] = useState(null);

  const loadOffers = useCallback(async () => {
    setLoading(true);
    setError(null);
    const res = await getOffers();
    if (res && res.success && Array.isArray(res.data)) {
      setOffers(res.data);
    } else if (res && !res.success) {
      setError(res.error || 'Failed to load offers');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadOffers();
  }, [loadOffers]);

  async function handleAccept(id) {
    setUpdatingId(id);
    const res = await acceptOffer(id);
    if (res && res.success) {
      setOffers(prev => prev.map(o => o.id === id ? { ...o, status: 'ACCEPTED' } : o));
    } else {
      alert(res?.error || 'Failed to accept offer');
    }
    setUpdatingId(null);
  }

  async function handleReject(id) {
    setUpdatingId(id);
    const res = await rejectOffer(id);
    if (res && res.success) {
      setOffers(prev => prev.map(o => o.id === id ? { ...o, status: 'REJECTED' } : o));
    } else {
      alert(res?.error || 'Failed to decline offer');
    }
    setUpdatingId(null);
  }

  const normStatus = (s) => (s || '').toLowerCase();
  const filtered = filter === 'all' ? offers : offers.filter(o => normStatus(o.status) === filter);

  const tabs = [
    { label: 'All', value: 'all', count: offers.length },
    { label: 'Pending', value: 'pending', count: offers.filter(o => normStatus(o.status) === 'pending').length },
    { label: 'Accepted', value: 'accepted', count: offers.filter(o => normStatus(o.status) === 'accepted').length },
    { label: 'Rejected', value: 'rejected', count: offers.filter(o => normStatus(o.status) === 'rejected').length },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Offers & Negotiations</h1>
        <p className="text-gray-500 text-sm mt-1">Review incoming buyer offers and manage negotiations</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-2 flex-wrap">
        {tabs.map(tab => (
          <button
            key={tab.value}
            onClick={() => setFilter(tab.value)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              filter === tab.value
                ? 'bg-green-800 text-white shadow-sm'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-green-300'
            }`}
          >
            {tab.label}
            <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
              filter === tab.value ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-500'
            }`}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingState />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No offers in this category"
          description="When buyers make offers on your listings, they will appear here."
          action={<Link to="/sell" className="btn-primary btn-sm">Create a Listing</Link>}
        />
      ) : (
        <div className="space-y-4">
          {filtered.map(offer => {
            const price = offer.price_per_unit || offer.offered_price || 0;
            const total = offer.total_value || (price * (offer.quantity || 0));
            const status = normStatus(offer.status);

            return (
              <div key={offer.id} className="card hover:shadow-md transition-shadow">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  {/* Left: Offer details */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <h3 className="font-bold text-gray-900">{offer.buyer_name || offer.buyer || 'Buyer Offer'}</h3>
                      <StatusBadge status={offer.status} />
                    </div>
                    <p className="text-sm text-gray-600">
                      {offer.crop_name || offer.crop || 'Produce'} · {offer.quantity} quintals
                    </p>

                    {/* Price breakdown */}
                    <div className="flex items-center gap-4 mt-3 flex-wrap">
                      <div className="flex items-center gap-1.5">
                        <IndianRupee className="w-4 h-4 text-green-600" />
                        <span className="font-bold text-green-800 text-lg">
                          ₹{Number(price).toLocaleString('en-IN')}
                        </span>
                        <span className="text-gray-400 text-sm">per quintal</span>
                      </div>
                      <div className="text-sm text-gray-500">
                        Total: <span className="font-semibold text-gray-800">₹{Number(total).toLocaleString('en-IN')}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 text-xs text-gray-400 mt-2">
                      <Clock className="w-3.5 h-3.5" />
                      Received {offer.created_at ? new Date(offer.created_at).toLocaleDateString('en-IN') : 'recently'}
                      {offer.expires_at && ` · Expires ${new Date(offer.expires_at).toLocaleDateString('en-IN')}`}
                    </div>
                  </div>

                  {/* Right: Actions */}
                  {status === 'pending' && (
                    <div className="flex flex-col gap-2 min-w-fit">
                      <button
                        onClick={() => handleAccept(offer.id)}
                        disabled={updatingId === offer.id}
                        className="btn-primary btn-sm flex items-center gap-2 disabled:opacity-60"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        Accept Offer
                      </button>
                      <button
                        onClick={() => handleReject(offer.id)}
                        disabled={updatingId === offer.id}
                        className="btn-secondary btn-sm flex items-center gap-2 text-red-600 border-red-200 hover:bg-red-50 disabled:opacity-60"
                      >
                        <XCircle className="w-4 h-4" />
                        Decline
                      </button>
                    </div>
                  )}

                  {status === 'accepted' && (
                    <Link to="/transactions" className="btn-secondary btn-sm flex items-center gap-2">
                      <Eye className="w-4 h-4" />
                      View Order
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
