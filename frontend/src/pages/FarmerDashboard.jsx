// =============================================================
// Farmer Dashboard
// Main page for logged-in farmers
// =============================================================

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  IndianRupee, Package, FileText, Wallet,
  TrendingUp, TrendingDown, Minus, MapPin, Star,
  ArrowUpRight, Warehouse, Clock, CheckCircle2
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { useAuth } from '../hooks/useAuth';
import { useLanguage } from '../hooks/useLanguage';
import { getPrices, getTrend, getPriceHistory } from '../services/api';
import { DEMO_BUYERS, DEMO_STORAGE, DEMO_LOTS } from '../data/demoData';
import { TrendBadge, VerifiedBadge, StatusBadge } from '../components/Badges';
import { LoadingState } from '../components/States';

// ---- Summary Card ----
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

// ---- Trend Info Box ----
function TrendInfoBox({ trendData, crop }) {
  if (!trendData) return null;
  const { trend, percentage_change, explanation } = trendData;

  const bg = trend === 'RISING' ? 'bg-green-50 border-green-200'
    : trend === 'FALLING' ? 'bg-red-50 border-red-200'
    : 'bg-amber-50 border-amber-200';

  const Icon = trend === 'RISING' ? TrendingUp
    : trend === 'FALLING' ? TrendingDown
    : Minus;

  const iconColor = trend === 'RISING' ? 'text-green-600'
    : trend === 'FALLING' ? 'text-red-600'
    : 'text-amber-600';

  return (
    <div className={`rounded-xl border p-4 ${bg}`}>
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 mt-0.5 ${iconColor} flex-shrink-0`} />
        <div>
          <p className="font-semibold text-gray-800 text-sm">{explanation}</p>
          <p className="text-xs text-gray-500 mt-1">
            Rule-Based Signal — calculated from 7-day price arithmetic. Not AI prediction.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function FarmerDashboard() {
  const { user } = useAuth();
  const { greeting } = useLanguage();
  const [prices, setPrices] = useState([]);
  const [trendData, setTrendData] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('Onion');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const [priceRes, trendRes, histRes] = await Promise.all([
        getPrices(),
        getTrend(selectedCrop, 'Lasalgaon'),
        getPriceHistory(selectedCrop, 'Lasalgaon', 14),
      ]);
      if (priceRes.success) setPrices(priceRes.data);
      if (trendRes.success) setTrendData(trendRes.data);
      if (histRes.success) setPriceHistory(histRes.data);
      setLoading(false);
    }
    loadData();
  }, [selectedCrop]);

  const movingAvg = trendData?.moving_average || 0;

  // Recent activity feed
  const activity = [
    { icon: Package, label: 'Lot listed: 500 qtl Onion', time: '1 day ago', color: 'bg-green-100 text-green-700' },
    { icon: FileText, label: 'Offer received from Mehta Traders', time: '1 day ago', color: 'bg-blue-100 text-blue-700' },
    { icon: CheckCircle2, label: 'Offer accepted — Pune Agro Exports', time: '5 days ago', color: 'bg-teal-100 text-teal-700' },
    { icon: Wallet, label: 'Payment received: ₹2,58,000', time: '2 days ago', color: 'bg-amber-100 text-amber-700' },
  ];

  const crops = ['Onion', 'Tomato', 'Soybean', 'Cotton'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {greeting}, {user?.name?.split(' ')[0]} 👋
          </h1>
          <div className="flex items-center gap-1.5 text-gray-500 text-sm mt-1">
            <MapPin className="w-4 h-4" />
            {user?.location || 'Nashik, Maharashtra'}
          </div>
        </div>
        <Link to="/sell" className="btn-primary flex items-center gap-2 whitespace-nowrap">
          + List Produce
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="Today's Best Price" value="₹1,920" sub="Onion — Lasalgaon" icon={IndianRupee} color="bg-green-100 text-green-700" />
        <SummaryCard title="Active Listings" value="2" sub="500 qtl Onion, 80 qtl Tomato" icon={Package} color="bg-blue-100 text-blue-700" />
        <SummaryCard title="Offers Received" value="3" sub="2 pending, 1 accepted" icon={FileText} color="bg-purple-100 text-purple-700" />
        <SummaryCard title="Pending Payments" value="₹2.3L" sub="1 transaction pending" icon={Wallet} color="bg-amber-100 text-amber-700" />
      </div>

      {/* Main content grid */}
      <div className="grid lg:grid-cols-3 gap-6">

        {/* LEFT: Market Prices + Trend Chart */}
        <div className="lg:col-span-2 space-y-6">

          {/* Crop selector + Trend */}
          <div className="card">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Price Trend</h2>
                <p className="text-xs text-gray-400 mt-0.5">7-day rule-based signal — not AI prediction</p>
              </div>
              <div className="flex gap-2 flex-wrap">
                {crops.map(crop => (
                  <button
                    key={crop}
                    onClick={() => setSelectedCrop(crop)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                      selectedCrop === crop
                        ? 'bg-green-800 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {crop}
                  </button>
                ))}
              </div>
            </div>

            {loading ? <LoadingState message="Loading price data..." /> : (
              <>
                {/* Chart */}
                <div className="h-52">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={priceHistory}>
                      <XAxis
                        dataKey="date"
                        tick={{ fontSize: 10, fill: '#9ca3af' }}
                        tickFormatter={(d) => d.slice(5)}
                      />
                      <YAxis
                        tick={{ fontSize: 10, fill: '#9ca3af' }}
                        tickFormatter={(v) => `₹${v.toLocaleString('en-IN')}`}
                        width={70}
                      />
                      <Tooltip
                        formatter={(v) => [`₹${v.toLocaleString('en-IN')}`, 'Price']}
                        labelFormatter={(l) => `Date: ${l}`}
                        contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb', fontSize: '13px' }}
                      />
                      {movingAvg > 0 && (
                        <ReferenceLine
                          y={movingAvg}
                          stroke="#d97706"
                          strokeDasharray="5 5"
                          label={{ value: '7d avg', position: 'insideTopRight', fontSize: 10, fill: '#d97706' }}
                        />
                      )}
                      <Line
                        type="monotone"
                        dataKey="price"
                        stroke="#2D6A4F"
                        strokeWidth={2.5}
                        dot={false}
                        activeDot={{ r: 5, fill: '#2D6A4F' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Trend stats */}
                {trendData && (
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500 mb-1">Current Price</p>
                      <p className="text-lg font-bold text-green-800">₹{trendData.current_price?.toLocaleString('en-IN')}</p>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500 mb-1">7-Day Average</p>
                      <p className="text-lg font-bold text-gray-700">₹{trendData.moving_average?.toLocaleString('en-IN')}</p>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500 mb-1">Change</p>
                      <TrendBadge trend={trendData.trend} change={trendData.percentage_change} />
                    </div>
                  </div>
                )}

                {/* Recommended action */}
                <div className="mt-4">
                  <TrendInfoBox trendData={trendData} crop={selectedCrop} />
                </div>
              </>
            )}
          </div>

          {/* Market Prices Table */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">Today's Market Prices</h2>
              <Link to="/prices" className="text-green-700 text-sm font-semibold flex items-center gap-1 hover:underline">
                View All <ArrowUpRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-2 text-gray-500 font-medium">Crop</th>
                    <th className="text-left py-2 text-gray-500 font-medium">Market</th>
                    <th className="text-right py-2 text-gray-500 font-medium">Price</th>
                    <th className="text-right py-2 text-gray-500 font-medium hidden sm:table-cell">Change</th>
                    <th className="text-center py-2 text-gray-500 font-medium">Trend</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {prices.slice(0, 8).map(p => (
                    <tr key={p.id} className="hover:bg-green-50/30 transition-colors">
                      <td className="py-3 font-semibold text-gray-800">{p.crop}</td>
                      <td className="py-3 text-gray-600">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-gray-400" />
                          {p.market}
                        </span>
                      </td>
                      <td className="py-3 text-right font-bold text-green-800">
                        ₹{p.modal_price.toLocaleString('en-IN')}
                      </td>
                      <td className="py-3 text-right hidden sm:table-cell">
                        <span className={p.change_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {p.change_pct >= 0 ? '+' : ''}{p.change_pct}%
                        </span>
                      </td>
                      <td className="py-3 text-center">
                        <TrendBadge trend={p.trend} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* RIGHT: Buyers + Storage + Activity */}
        <div className="space-y-6">
          {/* Nearby Buyers */}
          <div className="card">
            <h2 className="text-base font-bold text-gray-900 mb-4">Nearby Buyers</h2>
            <div className="space-y-3">
              {DEMO_BUYERS.slice(0, 3).map(buyer => (
                <div key={buyer.id} className="border border-gray-100 rounded-xl p-3 hover:border-green-200 transition-colors">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{buyer.name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{buyer.type} · {buyer.crops.join(', ')}</p>
                      <div className="flex items-center gap-2 mt-1.5">
                        {buyer.verified && <VerifiedBadge />}
                        <span className="flex items-center gap-0.5 text-xs text-amber-600">
                          <Star className="w-3 h-3 fill-amber-500 stroke-amber-500" />
                          {buyer.rating}
                        </span>
                        <span className="text-xs text-gray-400">{buyer.distance_km} km</span>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="text-sm font-bold text-green-800">₹{buyer.offer_price.toLocaleString('en-IN')}</p>
                      <p className="text-xs text-gray-400">/qtl</p>
                    </div>
                  </div>
                  <Link to="/matches" className="btn-primary btn-sm w-full mt-2 text-center text-xs block">
                    Make Offer
                  </Link>
                </div>
              ))}
            </div>
            <Link to="/matches" className="text-green-700 text-sm font-semibold flex items-center justify-center gap-1 mt-3 hover:underline">
              Find More Buyers <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Nearby Storage */}
          <div className="card">
            <h2 className="text-base font-bold text-gray-900 mb-4">Nearby Storage</h2>
            <div className="space-y-3">
              {DEMO_STORAGE.slice(0, 2).map(s => (
                <div key={s.id} className="border border-gray-100 rounded-xl p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Warehouse className="w-4 h-4 text-gray-400" />
                    <p className="font-semibold text-gray-800 text-sm">{s.name}</p>
                  </div>
                  <p className="text-xs text-gray-500">{s.type} · {s.distance_km} km away</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-gray-600">
                      <span className="font-semibold text-green-700">{s.available}T</span> available of {s.capacity}T
                    </span>
                    <span className="badge-green text-xs">₹{s.price_per_day}/T/day</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <h2 className="text-base font-bold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {activity.map((item, i) => {
                const Icon = item.icon;
                return (
                  <div key={i} className="flex items-start gap-3">
                    <div className={`w-8 h-8 ${item.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-700 font-medium">{item.label}</p>
                      <div className="flex items-center gap-1 text-xs text-gray-400 mt-0.5">
                        <Clock className="w-3 h-3" />
                        {item.time}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
