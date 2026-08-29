// =============================================================
// Buyer Dashboard
// =============================================================

import { useState, useEffect } from 'react';
import { Search, ShoppingBag, FileText, CheckCircle2, TrendingUp, MapPin, Star } from 'lucide-react';
import { getLots, createOffer } from '../services/api';
import { StatusBadge, VerifiedBadge } from '../components/Badges';
import { LoadingState } from '../components/States';
import { useAuth } from '../hooks/useAuth';

function SummaryCard({ title, value, sub, icon: Icon, color }) {
  return (
    <div className="card flex items-start gap-4">
      <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center flex-shrink-0`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-0.5">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

export default function BuyerDashboard() {
  const { user } = useAuth();
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [cropFilter, setCropFilter] = useState('All');
  const [offeringSent, setOfferingSent] = useState({});

  useEffect(() => {
    async function load() {
      const res = await getLots();
      if (res.success) setLots(res.data);
      setLoading(false);
    }
    load();
  }, []);

  const lotList = Array.isArray(lots) ? lots : [];
  const filtered = lotList.filter(l => {
    if (!l) return false;
    if (cropFilter !== 'All' && l.crop !== cropFilter) return false;
    if (searchTerm && !l.crop?.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !l.location?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return l.status === 'active' || l.status === 'matched';
  });

  async function handleOffer(lot) {
    setOfferingSent(p => ({ ...p, [lot.id]: 'sending' }));
    await createOffer({ lot_id: lot.id, crop: lot.crop, quantity: lot.quantity, offered_price: lot.expected_price * 0.97 });
    setOfferingSent(p => ({ ...p, [lot.id]: 'sent' }));
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Buyer Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Browse available produce lots from farmers and FPOs</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="Available Lots" value={lotList.filter(l => l?.status === 'active').length} sub="Ready to purchase" icon={ShoppingBag} color="bg-blue-100 text-blue-700" />
        <SummaryCard title="Active Offers" value="3" sub="Awaiting farmer response" icon={FileText} color="bg-amber-100 text-amber-700" />
        <SummaryCard title="Accepted Offers" value="1" sub="In progress" icon={CheckCircle2} color="bg-green-100 text-green-700" />
        <SummaryCard title="Transactions" value="2" sub="Completed" icon={TrendingUp} color="bg-purple-100 text-purple-700" />
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input className="input pl-10" placeholder="Search by crop or location..."
              value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
          </div>
          <select className="input sm:w-44" value={cropFilter} onChange={(e) => setCropFilter(e.target.value)}>
            {['All', 'Onion', 'Tomato', 'Soybean', 'Cotton', 'Wheat'].map(c => <option key={c}>{c}</option>)}
          </select>
        </div>
      </div>

      {/* Lot cards */}
      {loading ? <LoadingState /> : (
        <>
          <p className="text-sm text-gray-500">{filtered.length} lots available</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map(lot => (
              <div key={lot.id} className="card-hover">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">{lot.crop}</h3>
                    <p className="text-gray-500 text-sm mt-0.5">{lot.farmer}</p>
                  </div>
                  <StatusBadge status={lot.status} />
                </div>

                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="bg-gray-50 rounded-xl p-3">
                    <p className="text-xs text-gray-500">Quantity</p>
                    <p className="font-bold text-gray-900 mt-0.5">{lot.quantity} {lot.unit}</p>
                  </div>
                  <div className="bg-green-50 rounded-xl p-3">
                    <p className="text-xs text-gray-500">Expected Price</p>
                    <p className="font-bold text-green-800 mt-0.5">₹{lot.expected_price?.toLocaleString('en-IN')}<span className="text-xs font-normal text-gray-400">/qtl</span></p>
                  </div>
                </div>

                <div className="flex items-center gap-3 mb-4 text-sm">
                  <span className="badge-blue">Grade {lot.grade}</span>
                  <span className="flex items-center gap-1 text-gray-500">
                    <MapPin className="w-3.5 h-3.5" />{lot.location}
                  </span>
                </div>

                {lot.available_date && (
                  <p className="text-xs text-gray-400 mb-4">
                    Available from: {new Date(lot.available_date).toLocaleDateString('en-IN')}
                  </p>
                )}

                {offeringSent[lot.id] === 'sent' ? (
                  <div className="py-2.5 bg-green-50 text-green-700 font-semibold text-sm text-center rounded-xl flex items-center justify-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Offer Sent!
                  </div>
                ) : (
                  <button
                    onClick={() => handleOffer(lot)}
                    disabled={offeringSent[lot.id] === 'sending'}
                    className="btn-primary w-full disabled:opacity-60"
                  >
                    {offeringSent[lot.id] === 'sending' ? 'Sending...' : 'Make an Offer'}
                  </button>
                )}
              </div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="card text-center py-12">
              <p className="text-gray-500">No lots match your search. Try changing filters.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
