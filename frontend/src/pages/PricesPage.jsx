// =============================================================
// Market Prices Page
// Full price comparison with filters and charts
// Uses Truthful Mandi Arrival Rates from Government & Database
// =============================================================

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Search, Filter, MapPin, Calendar, RefreshCw } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { getLivePrices, getPriceHistory } from '../services/api';
import { TrendBadge } from '../components/Badges';
import { LoadingState, ErrorState } from '../components/States';
import { getCropImage } from '../utils/cropImages';

const CROPS = ['All', 'Onion', 'Tomato', 'Soybean', 'Cotton', 'Wheat', 'Potato', 'Chilli', 'Rice', 'Maize'];
const REGIONS = ['All', 'Nashik', 'Lasalgaon', 'Pune', 'Ahmednagar', 'Solapur', 'Aurangabad', 'Bengaluru', 'Mysuru'];

export default function PricesPage() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSource, setDataSource] = useState('data.gov.in (Agmarknet)');
  const [isLive, setIsLive] = useState(false);

  const [cropFilter, setCropFilter] = useState('All');
  const [marketFilter, setMarketFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCrop, setSelectedCrop] = useState('Onion');
  const [priceHistory, setPriceHistory] = useState([]);
  const [histLoading, setHistLoading] = useState(false);

  const loadPrices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getLivePrices({
        crop: cropFilter === 'All' ? null : cropFilter,
        market: marketFilter === 'All' ? null : marketFilter,
        limit: 100,
      });

      if (res && res.success && Array.isArray(res.data)) {
        // Normalize field names
        const normalized = res.data.map(p => ({
          id: p.id || `${p.commodity || p.crop}-${p.market}-${p.arrival_date || p.price_date}`,
          crop: p.commodity || p.crop || 'Produce',
          market: p.market || 'Mandi',
          district: p.district || '',
          state: p.state || 'Maharashtra',
          min_price: Number(p.min_price || 0),
          modal_price: Number(p.modal_price || 0),
          max_price: Number(p.max_price || 0),
          volume: p.volume || p.volume_tonnes || null,
          arrival_date: p.arrival_date || p.price_date || '',
          trend: p.trend || 'STABLE',
          change_pct: p.change_pct,
        }));
        setPrices(normalized);
        setIsLive(Boolean(res.is_live));
        if (res.source) setDataSource(res.source);
      } else {
        setError(res?.error || 'Could not load price data.');
      }
    } catch {
      setError('Price data is temporarily unavailable. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [cropFilter, marketFilter]);

  const loadHistory = useCallback(async (crop) => {
    setHistLoading(true);
    try {
      const res = await getPriceHistory(crop, null, 15);
      if (res && res.success && Array.isArray(res.data)) {
        setPriceHistory(res.data);
      }
    } catch {
      // safe fallback
    } finally {
      setHistLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPrices();
  }, [loadPrices]);

  useEffect(() => {
    loadHistory(selectedCrop);
  }, [selectedCrop, loadHistory]);

  const filtered = useMemo(() => {
    const list = Array.isArray(prices) ? prices : [];
    let data = [...list];
    if (cropFilter !== 'All') data = data.filter(p => p && p.crop?.toLowerCase().includes(cropFilter.toLowerCase()));
    if (marketFilter !== 'All') data = data.filter(p => p && (p.market?.toLowerCase().includes(marketFilter.toLowerCase()) || p.district?.toLowerCase().includes(marketFilter.toLowerCase())));
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      data = data.filter(p => p && (p.crop?.toLowerCase().includes(q) || p.market?.toLowerCase().includes(q) || p.district?.toLowerCase().includes(q)));
    }
    return data;
  }, [prices, cropFilter, marketFilter, searchTerm]);

  // Best price for the selected crop
  const bestPrice = useMemo(() => {
    return prices
      .filter(p => p && p.crop?.toLowerCase() === selectedCrop.toLowerCase())
      .sort((a, b) => (Number(b.modal_price) || 0) - (Number(a.modal_price) || 0))[0];
  }, [prices, selectedCrop]);

  // Market comparison data for bar chart
  const marketComparison = useMemo(() => {
    return prices
      .filter(p => p && p.crop?.toLowerCase() === selectedCrop.toLowerCase() && p.modal_price > 0)
      .slice(0, 8)
      .map(p => ({ market: p.market.split('(')[0].trim(), price: Number(p.modal_price) || 0 }));
  }, [prices, selectedCrop]);

  // Best price overall for highlight in table
  const maxPriceValue = useMemo(() => {
    return filtered.length > 0 ? Math.max(...filtered.map(p => Number(p.modal_price) || 0)) : 0;
  }, [filtered]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <p className="section-label">Mandi Live Insights</p>
            {isLive ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-bold bg-green-100 text-green-800 px-2 py-0.5 rounded-full border border-green-200">
                <span className="w-1.5 h-1.5 rounded-full bg-green-600 animate-pulse" /> Live Government Data
              </span>
            ) : (
              <span className="text-[11px] font-bold bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full">
                Verified Mandi Database
              </span>
            )}
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">APMC Mandi Modal Prices</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Daily government arrival rates from agricultural produce markets ({dataSource})
          </p>
        </div>

        <button
          onClick={loadPrices}
          className="btn-secondary btn-sm flex items-center gap-2 text-xs self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Prices
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input pl-10 text-sm"
              placeholder="Search commodity or market..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Crop filter */}
          <select
            className="input sm:w-44 text-sm"
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
          >
            {CROPS.map(c => <option key={c}>{c}</option>)}
          </select>

          {/* Market filter */}
          <select
            className="input sm:w-44 text-sm"
            value={marketFilter}
            onChange={(e) => setMarketFilter(e.target.value)}
          >
            {REGIONS.map(m => <option key={m}>{m}</option>)}
          </select>
        </div>

        {/* Active filters summary */}
        {(cropFilter !== 'All' || marketFilter !== 'All' || searchTerm) && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">Showing {filtered.length} matching observations</span>
            <button
              onClick={() => { setCropFilter('All'); setMarketFilter('All'); setSearchTerm(''); }}
              className="text-sm text-green-700 font-semibold hover:underline ml-auto"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* 15-day trend chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="section-label">Dated Series</p>
              <h2 className="text-base font-bold text-gray-900">Historical Price Trend</h2>
              <p className="text-xs text-gray-400 mt-0.5">Recorded daily observations</p>
            </div>
            <select
              className="input text-sm w-36 py-1.5 px-3 min-h-[36px]"
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
            >
              {['Onion', 'Tomato', 'Soybean', 'Cotton', 'Wheat', 'Potato', 'Chilli', 'Rice'].map(c => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>

          {histLoading ? <LoadingState message="Loading trend history..." /> : priceHistory.length === 0 ? (
            <div className="h-52 flex flex-col items-center justify-center text-center text-gray-400 text-xs px-4 bg-gray-50/50 rounded-xl">
              <Calendar className="w-8 h-8 mb-2 text-gray-300" />
              <span>Historical trend records are available as daily market observations arrive.</span>
            </div>
          ) : (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceHistory}>
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => String(d || '').slice(5)} />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${Number(v || 0).toLocaleString('en-IN')}`} width={70} />
                  <Tooltip
                    formatter={(v) => [`₹${Number(v || 0).toLocaleString('en-IN')}`, 'Modal Price']}
                    labelFormatter={(l) => `Arrival Date: ${l}`}
                    contentStyle={{ borderRadius: '12px', fontSize: '13px' }}
                  />
                  <Line type="monotone" dataKey="price" stroke="#2D6A4F" strokeWidth={2.5} dot={{ r: 3, fill: '#2D6A4F' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {bestPrice && (
            <div className="mt-4 bg-green-50 border border-green-100 rounded-xl p-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img
                  src={getCropImage(bestPrice.crop)}
                  alt={bestPrice.crop}
                  className="w-10 h-10 rounded-lg object-cover border border-green-200 shadow-2xs"
                />
                <div>
                  <p className="text-xs text-gray-500 font-semibold">Highest reported modal rate</p>
                  <p className="font-bold text-green-800">{bestPrice.crop} — {bestPrice.market}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-green-800 tracking-tight">₹{Number(bestPrice.modal_price || 0).toLocaleString('en-IN')}</p>
                <p className="text-xs text-gray-400">per quintal ({bestPrice.arrival_date || 'Today'})</p>
              </div>
            </div>
          )}
        </div>

        {/* Market comparison bar chart */}
        <div className="card">
          <div className="mb-4">
            <p className="section-label">Cross-Mandi Benchmark</p>
            <h2 className="text-base font-bold text-gray-900 mb-1">Market Comparison</h2>
            <p className="text-xs text-gray-400 mb-2">Modal price across APMCs for {selectedCrop}</p>
          </div>
          {marketComparison.length > 0 ? (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={marketComparison} barSize={32}>
                  <XAxis dataKey="market" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${Number(v || 0).toLocaleString('en-IN')}`} width={70} />
                  <Tooltip
                    formatter={(v) => [`₹${Number(v || 0).toLocaleString('en-IN')}`, 'Modal Price']}
                    contentStyle={{ borderRadius: '12px', fontSize: '13px' }}
                  />
                  <Bar dataKey="price" fill="#2D6A4F" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-52 flex items-center justify-center text-gray-400 text-xs bg-gray-50/50 rounded-xl">
              No comparison data currently available for {selectedCrop}.
            </div>
          )}
        </div>
      </div>

      {/* Price Table */}
      {loading ? <LoadingState /> : error ? (
        <ErrorState message={error} onRetry={loadPrices} />
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-white sticky left-0">
            <div>
              <h2 className="font-bold text-gray-900">Mandi Price Directory</h2>
              <p className="text-xs text-gray-400 mt-0.5">Showing {filtered.length} verified observations</p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#f0f9f4]">
                <tr>
                  <th className="text-left px-5 py-3 text-sm font-semibold text-green-800">Crop</th>
                  <th className="text-left px-5 py-3 text-sm font-semibold text-green-800">APMC Mandi</th>
                  <th className="text-left px-5 py-3 text-sm font-semibold text-green-800 hidden sm:table-cell">Arrival Date</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-green-800">Min</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-green-800">Modal</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-green-800">Max</th>
                  <th className="text-center px-5 py-3 text-sm font-semibold text-green-800">Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 bg-white">
                {filtered.map(p => {
                  const modal = Number(p.modal_price) || 0;
                  const isBest = modal === maxPriceValue && filtered.length > 1;
                  return (
                    <tr key={p.id} className={`transition-colors ${isBest ? 'bg-green-50/50' : 'hover:bg-green-50/30'}`}>
                      <td className="px-5 py-3.5 font-semibold text-gray-800">
                        <div className="flex items-center gap-2.5">
                          {isBest && <div className="absolute left-0 w-1 h-10 bg-green-500 rounded-r" />}
                          <img
                            src={getCropImage(p.crop)}
                            alt={p.crop}
                            className="w-8 h-8 rounded-md object-cover flex-shrink-0 border border-gray-100 shadow-sm"
                          />
                          <span>{p.crop}</span>
                          {isBest && <span className="ml-1 text-[10px] font-bold bg-green-200 text-green-800 px-1.5 py-0.5 rounded-full">BEST</span>}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-gray-600">
                        <span className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                          <span>{p.market} {p.district ? `(${p.district})` : ''}</span>
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-gray-500 text-xs hidden sm:table-cell">
                        {p.arrival_date || '—'}
                      </td>
                      <td className="px-5 py-3.5 text-right text-gray-500">₹{Number(p.min_price || 0).toLocaleString('en-IN')}</td>
                      <td className={`px-5 py-3.5 text-right font-bold ${isBest ? 'text-green-700 text-lg' : 'text-gray-900'}`}>
                        ₹{modal.toLocaleString('en-IN')}
                      </td>
                      <td className="px-5 py-3.5 text-right text-gray-500">₹{Number(p.max_price || 0).toLocaleString('en-IN')}</td>
                      <td className="px-5 py-3.5 text-center">
                        <TrendBadge trend={p.trend} change={p.change_pct} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {filtered.length === 0 && (
            <div className="px-6 py-12 text-center text-gray-400 text-sm">
              No mandi price records match your selected filters.
            </div>
          )}
        </div>
      )}

      <p className="text-xs text-gray-400 text-center">
        * All mandi prices are reported in ₹ per quintal (100 kg) according to Agmarknet / Ministry of Agriculture standard reporting formats.
      </p>
    </div>
  );
}
