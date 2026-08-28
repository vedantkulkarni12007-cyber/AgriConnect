// =============================================================
// Landing Page
// The first page visitors see. Shows the product pitch.
// =============================================================

import { Link } from 'react-router-dom';
import {
  TrendingUp, TrendingDown, Users, ShieldCheck,
  Truck, BarChart2, ArrowRight, CheckCircle2,
  MapPin, Sprout, Star, ArrowUpRight
} from 'lucide-react';
import { DEMO_PRICES } from '../data/demoData';
import { TrendBadge } from '../components/Badges';

// -------------------------------------------------------
// HERO SECTION
// -------------------------------------------------------
function Hero() {
  return (
    <section className="bg-gradient-to-b from-green-900 to-green-800 text-white pt-16 pb-24 px-4">
      <div className="max-w-6xl mx-auto text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-white/10 border border-white/20 rounded-full px-4 py-1.5 text-sm font-medium mb-6">
          <Sprout className="w-4 h-4 text-green-300" />
          Smart India Hackathon 2024
        </div>

        {/* Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6 text-balance">
          Know Your Price.<br />
          Find Your Buyer.<br />
          <span className="text-green-300">Sell Smarter.</span>
        </h1>

        <p className="text-lg sm:text-xl text-green-100 max-w-2xl mx-auto mb-10 leading-relaxed">
          KrishiLink helps farmers discover better market prices, connect with
          verified buyers, and keep track of every stage of a sale — all in one place.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/prices" className="btn-accent flex items-center gap-2 text-base w-full sm:w-auto justify-center">
            <BarChart2 className="w-5 h-5" />
            Explore Market Prices
          </Link>
          <Link to="/register" className="btn-secondary flex items-center gap-2 text-base w-full sm:w-auto justify-center border-white text-white hover:bg-white hover:text-green-800">
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-16 max-w-lg mx-auto">
          {[
            { value: '200+', label: 'Markets Tracked' },
            { value: '8', label: 'Major Crops' },
            { value: '100%', label: 'Transparent' },
          ].map(stat => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-bold text-green-300">{stat.value}</div>
              <div className="text-xs text-green-200 mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// -------------------------------------------------------
// PROBLEM SECTION
// -------------------------------------------------------
function Problem() {
  const problems = [
    {
      icon: '📊',
      title: 'Price Uncertainty',
      desc: 'Farmers often don\'t know the current price in nearby mandis and may accept less than market rate.',
    },
    {
      icon: '🤝',
      title: 'Fragmented Buyers',
      desc: 'Finding trustworthy buyers is difficult. Information about who is buying, at what price, is scattered.',
    },
    {
      icon: '⚡',
      title: 'Distress Sales',
      desc: 'Urgent cash needs force farmers to sell at low prices, sometimes below their cost of production.',
    },
    {
      icon: '📦',
      title: 'Small Quantities',
      desc: 'Individual farmers with small lots have less bargaining power compared to aggregated groups.',
    },
    {
      icon: '📄',
      title: 'Verbal Agreements',
      desc: 'Deals made verbally have no record, making it hard to resolve disputes about price or quantity.',
    },
  ];

  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <span className="badge-red text-sm mb-3">The Problem</span>
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mt-2">
            Challenges Farmers Face Every Day
          </h2>
          <p className="text-gray-500 mt-3 max-w-xl mx-auto">
            Despite growing crops, farmers often receive less than fair value due to information gaps and lack of market access.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
          {problems.map((p) => (
            <div key={p.title} className="card text-center hover:border-green-200 transition-all">
              <div className="text-4xl mb-3">{p.icon}</div>
              <h3 className="font-bold text-gray-800 mb-2">{p.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{p.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// -------------------------------------------------------
// SOLUTION SECTION
// -------------------------------------------------------
function Solution() {
  const solutions = [
    {
      icon: BarChart2,
      color: 'bg-green-100 text-green-700',
      title: 'Price Intelligence',
      desc: 'See real-time prices from multiple mandis. Compare easily to know where to sell.',
    },
    {
      icon: TrendingUp,
      color: 'bg-blue-100 text-blue-700',
      title: 'Trend Signals',
      desc: 'Know if prices are rising or falling based on 7-day price arithmetic — not guesswork.',
    },
    {
      icon: Users,
      color: 'bg-purple-100 text-purple-700',
      title: 'Buyer Matching',
      desc: 'Get matched to verified buyers based on crop, grade, quantity and location.',
    },
    {
      icon: Truck,
      color: 'bg-orange-100 text-orange-700',
      title: 'Logistics & Storage',
      desc: 'Locate nearby warehouses, cold storage and logistics options on an interactive map.',
    },
    {
      icon: ShieldCheck,
      color: 'bg-teal-100 text-teal-700',
      title: 'Transaction & Trust',
      desc: 'Track every step of a sale with a complete transparent record from offer to payment.',
    },
  ];

  return (
    <section className="py-20 px-4 bg-[#FAFAF7]">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <span className="badge-green text-sm mb-3">The Solution</span>
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mt-2">
            Everything a Farmer Needs in One Place
          </h2>
          <p className="text-gray-500 mt-3 max-w-xl mx-auto">
            KrishiLink gives you five core tools to earn better from every harvest.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
          {solutions.map((s) => {
            const Icon = s.icon;
            return (
              <div key={s.title} className="card-hover text-center">
                <div className={`w-12 h-12 ${s.color} rounded-xl flex items-center justify-center mx-auto mb-4`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="font-bold text-gray-800 mb-2">{s.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{s.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

// -------------------------------------------------------
// HOW IT WORKS SECTION
// -------------------------------------------------------
function HowItWorks() {
  const steps = [
    { step: '01', title: 'Check Prices',     desc: 'See today\'s prices across all nearby mandis for your crop.' },
    { step: '02', title: 'List Produce',     desc: 'Create a listing with your crop, quantity, grade and expected price.' },
    { step: '03', title: 'Find Buyers',      desc: 'Get matched to verified buyers based on your listing details.' },
    { step: '04', title: 'Receive an Offer', desc: 'Buyers submit offers. Review and accept or negotiate.' },
    { step: '05', title: 'Complete Sale',    desc: 'Track dispatch, payment, and get a full transaction record.' },
  ];

  return (
    <section id="how-it-works" className="py-20 px-4 bg-white">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <span className="badge-blue text-sm mb-3">How It Works</span>
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mt-2">
            Sell Your Crop in 5 Simple Steps
          </h2>
        </div>

        <div className="relative">
          {/* Connector line (desktop only) */}
          <div className="hidden lg:block absolute top-10 left-[10%] right-[10%] h-0.5 bg-green-100 z-0" />

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-6 relative z-10">
            {steps.map((s, i) => (
              <div key={s.step} className="text-center">
                <div className="w-16 h-16 bg-green-800 rounded-full flex items-center justify-center mx-auto mb-4 shadow-md">
                  <span className="text-white font-bold text-lg">{s.step}</span>
                </div>
                <h3 className="font-bold text-gray-800 mb-1">{s.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{s.desc}</p>
                {i < steps.length - 1 && (
                  <div className="lg:hidden flex justify-center mt-4">
                    <ArrowRight className="w-5 h-5 text-green-300 rotate-90" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="text-center mt-10">
          <Link to="/login" className="btn-primary inline-flex items-center gap-2">
            Start Your Journey
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}

// -------------------------------------------------------
// PRICE PREVIEW SECTION
// -------------------------------------------------------
function PricePreview() {
  const topPrices = DEMO_PRICES.slice(0, 6);

  return (
    <section className="py-20 px-4 bg-[#FAFAF7]">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10">
          <div>
            <span className="badge-yellow text-sm mb-2 block">Live Demo Data</span>
            <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">
              Today's Market Prices
            </h2>
            <p className="text-gray-500 text-sm mt-1">
              Sample mandi data — realistic prices for demonstration
            </p>
          </div>
          <Link to="/prices" className="btn-secondary btn-sm flex items-center gap-2 whitespace-nowrap">
            View All Prices
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-gray-100 shadow-sm bg-white">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-5 py-3.5 text-sm font-semibold text-gray-600">Crop</th>
                <th className="text-left px-5 py-3.5 text-sm font-semibold text-gray-600">Market</th>
                <th className="text-right px-5 py-3.5 text-sm font-semibold text-gray-600">Modal Price</th>
                <th className="text-right px-5 py-3.5 text-sm font-semibold text-gray-600 hidden sm:table-cell">Min / Max</th>
                <th className="text-center px-5 py-3.5 text-sm font-semibold text-gray-600">Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {topPrices.map((p) => (
                <tr key={p.id} className="hover:bg-green-50/30 transition-colors">
                  <td className="px-5 py-4 font-semibold text-gray-800">{p.crop}</td>
                  <td className="px-5 py-4 text-gray-600 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-gray-400" />
                    {p.market}
                  </td>
                  <td className="px-5 py-4 text-right font-bold text-green-800">
                    ₹{p.modal_price.toLocaleString('en-IN')}
                    <span className="text-gray-400 font-normal text-xs">/qtl</span>
                  </td>
                  <td className="px-5 py-4 text-right text-gray-500 text-sm hidden sm:table-cell">
                    ₹{p.min_price.toLocaleString('en-IN')} — ₹{p.max_price.toLocaleString('en-IN')}
                  </td>
                  <td className="px-5 py-4 text-center">
                    <TrendBadge trend={p.trend} change={p.change_pct} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-xs text-gray-400 mt-3 text-center">
          * Demo data only. Trend signals are calculated using 7-day price arithmetic — not AI prediction.
        </p>
      </div>
    </section>
  );
}

// -------------------------------------------------------
// TRUST SECTION
// -------------------------------------------------------
function TrustSection() {
  const features = [
    { icon: ShieldCheck, title: 'Verified Buyers', desc: 'Every buyer is reviewed before listing.' },
    { icon: CheckCircle2, title: 'Transparent Offers', desc: 'All offer details are visible and recorded.' },
    { icon: BarChart2, title: 'Transaction History', desc: 'Complete record of every deal.' },
    { icon: Star, title: 'Grievance System', desc: 'File and track disputes easily.' },
  ];

  return (
    <section className="py-20 px-4 bg-green-800 text-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <h2 className="text-3xl lg:text-4xl font-bold mb-3">
            Built on Trust and Transparency
          </h2>
          <p className="text-green-200 max-w-xl mx-auto">
            Every feature in KrishiLink is designed to give farmers information and confidence.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <div key={f.title} className="bg-white/10 rounded-2xl p-6 text-center border border-white/10">
                <Icon className="w-10 h-10 text-green-300 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">{f.title}</h3>
                <p className="text-green-200 text-sm leading-relaxed">{f.desc}</p>
              </div>
            );
          })}
        </div>

        <div className="text-center mt-12">
          <Link to="/register" className="btn-accent inline-flex items-center gap-2 text-base">
            Join KrishiLink Today
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}

// -------------------------------------------------------
// MAIN LANDING PAGE
// -------------------------------------------------------
export default function LandingPage() {
  return (
    <div>
      <Hero />
      <Problem />
      <Solution />
      <HowItWorks />
      <PricePreview />
      <TrustSection />
    </div>
  );
}
