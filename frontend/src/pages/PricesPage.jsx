// =============================================================
// Market Prices Page
// Full price comparison with filters and charts
// =============================================================

import { useState, useEffect } from 'react';
import { Search, Filter, MapPin } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import { getPrices, getPriceHistory } from '../services/api';
import { TrendBadge } from '../components/Badges';
import { LoadingState, ErrorState } from '../components/States';

const CROPS = ['All', 'Onion', 'Tomato', 'Soybean', 'Cotton', 'Wheat', 'Potato', 'Chilli', 'Rice'];
const MARKETS = ['All', 'Nashik', 'Lasalgaon', 'Pune', 'Ahmednagar', 'Solapur', 'Aurangabad'];

export default function PricesPage() {
  const [prices, setPrices] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cropFilter, setCropFilter] = useState('All');
  const [marketFilter, setMarketFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCrop, setSelectedCrop] = useState('Onion');
  const [priceHistory, setPriceHistory] = useState([]);
  const [histLoading, setHistLoading] = useState(false);

  useEffect(() => {
    loadPrices();
  }, []);

  useEffect(() => {
    let data = [...prices];
    if (cropFilter !== 'All') data = data.filter(p => p.crop === cropFilter);
    if (marketFilter !== 'All') data = data.filter(p => p.market === marketFilter);
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      data = data.filter(p => p.crop.toLowerCase().includes(q) || p.market.toLowerCase().includes(q));
    }
    setFiltered(data);
  }, [prices, cropFilter, marketFilter, searchTerm]);

  useEffect(() => {
    loadHistory(selectedCrop);
  }, [selectedCrop]);

  async function loadPrices() {
    setLoading(true);
    setError(null);
    try {
      const res = await getPrices();
      if (res.success) {
        setPrices(res.data);
        setFiltered(res.data);
      } else {
        setError('Could not load price data.');
      }
    } catch {
      setError('Price data is temporarily unavailable. Please try again.');
    }
    setLoading(false);
  }

  async function loadHistory(crop) {
    setHistLoading(true);
    const res = await getPriceHistory(crop, null, 15);
    if (res.success) setPriceHistory(res.data);
    setHistLoading(false);
  }

  // Best price for the selected crop
  const bestPrice = prices
    .filter(p => p.crop === selectedCrop)
    .sort((a, b) => b.modal_price - a.modal_price)[0];

  // Market comparison data for bar chart
  const marketComparison = prices
    .filter(p => p.crop === selectedCrop)
    .map(p => ({ market: p.market, price: p.modal_price }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Today's Market Prices</h1>
        <p className="text-gray-500 text-sm mt-1">
          Current modal prices from mandis across Maharashtra — Demo Data
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input pl-10"
              placeholder="Search crop or market..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Crop filter */}
          <select
            className="input sm:w-44"
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
          >
            {CROPS.map(c => <option key={c}>{c}</option>)}
          </select>

          {/* Market filter */}
          <select
            className="input sm:w-44"
            value={marketFilter}
            onChange={(e) => setMarketFilter(e.target.value)}
          >
            {MARKETS.map(m => <option key={m}>{m}</option>)}
          </select>
        </div>

        {/* Active filters */}
        {(cropFilter !== 'All' || marketFilter !== 'All' || searchTerm) && (
          <div className="flex items-center gap-2 mt-3">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">Showing {filtered.length} results</span>
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
              <h2 className="text-base font-bold text-gray-900">15-Day Price Trend</h2>
              <p className="text-xs text-gray-400 mt-0.5">Historical modal prices</p>
            </div>
            <select
              className="input text-sm w-36"
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
            >
              {['Onion', 'Tomato', 'Soybean', 'Cotton'].map(c => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          {histLoading ? <LoadingState message="Loading chart..." /> : (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={priceHistory}>
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => d.slice(5)} />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${v.toLocaleString('en-IN')}`} width={70} />
                  <Tooltip
                    formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Price']}
                    contentStyle={{ borderRadius: '12px', fontSize: '13px' }}
                  />
                  <Line type="monotone" dataKey="price" stroke="#2D6A4F" strokeWidth={2.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          {bestPrice && (
            <div className="mt-4 bg-green-50 border border-green-100 rounded-xl p-3 flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500">Best price today</p>
                <p className="font-bold text-green-800">{bestPrice.market}</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-green-800">₹{bestPrice.modal_price.toLocaleString('en-IN')}</p>
                <p className="text-xs text-gray-400">per quintal</p>
              </div>
            </div>
          )}
        </div>

        {/* Market comparison bar chart */}
        <div className="card">
          <h2 className="text-base font-bold text-gray-900 mb-1">Market Comparison</h2>
          <p className="text-xs text-gray-400 mb-4">Modal price across markets for {selectedCrop}</p>
          {marketComparison.length > 0 ? (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={marketComparison} barSize={36}>
                  <XAxis dataKey="market" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${v.toLocaleString('en-IN')}`} width={70} />
                  <Tooltip
                    formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Price']}
                    contentStyle={{ borderRadius: '12px', fontSize: '13px' }}
                  />
                  <Bar dataKey="price" fill="#2D6A4F" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-52 flex items-center justify-center text-gray-400 text-sm">
              Select a crop to see comparison
            </div>
          )}
        </div>
      </div>

      {/* Price Table */}
      {loading ? <LoadingState /> : error ? (
        <ErrorState message={error} onRetry={loadPrices} />
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-bold text-gray-900">Price Details</h2>
            <p className="text-xs text-gray-400 mt-0.5">{filtered.length} records</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-5 py-3 text-sm font-semibold text-gray-600">Crop</th>
                  <th className="text-left px-5 py-3 text-sm font-semibold text-gray-600">Market</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-gray-600">Min</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-gray-600">Modal</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-gray-600">Max</th>
                  <th className="text-right px-5 py-3 text-sm font-semibold text-gray-600 hidden md:table-cell">Volume (T)</th>
                  <th className="text-center px-5 py-3 text-sm font-semibold text-gray-600">Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map(p => (
                  <tr key={p.id} className="hover:bg-green-50/30 transition-colors">
                    <td className="px-5 py-3.5 font-semibold text-gray-800">{p.crop}</td>
                    <td className="px-5 py-3.5 text-gray-600">
                      <span className="flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-gray-400" />
                        {p.market}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right text-gray-600">₹{p.min_price.toLocaleString('en-IN')}</td>
                    <td className="px-5 py-3.5 text-right font-bold text-green-800">₹{p.modal_price.toLocaleString('en-IN')}</td>
                    <td className="px-5 py-3.5 text-right text-gray-600">₹{p.max_price.toLocaleString('en-IN')}</td>
                    <td className="px-5 py-3.5 text-right text-gray-500 hidden md:table-cell">{p.volume}</td>
                    <td className="px-5 py-3.5 text-center">
                      <TrendBadge trend={p.trend} change={p.change_pct} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length === 0 && (
            <div className="px-6 py-12 text-center text-gray-400">
              No prices match your filters.
            </div>
          )}
        </div>
      )}

      <p className="text-xs text-gray-400 text-center">
        * All prices are in ₹ per quintal. Trend signals use 7-day arithmetic — not AI prediction. Source: Demo Data.
      </p>
    </div>
  );
}
