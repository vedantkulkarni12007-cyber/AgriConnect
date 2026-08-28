// =============================================================
// Transactions Page
// Shows transaction timeline and payment status
// =============================================================

import { useState, useEffect } from 'react';
import { CheckCircle2, Circle, Clock, IndianRupee, Package, Truck, Wallet } from 'lucide-react';
import { getTransactions } from '../services/api';
import { StatusBadge } from '../components/Badges';
import { LoadingState, EmptyState } from '../components/States';

// Stage definitions
const STAGES = [
  { key: 'offer_created',      label: 'Offer Created',       icon: Package },
  { key: 'offer_accepted',     label: 'Offer Accepted',      icon: CheckCircle2 },
  { key: 'produce_dispatched', label: 'Produce Dispatched',  icon: Truck },
  { key: 'payment_pending',    label: 'Payment Pending',     icon: Clock },
  { key: 'payment_received',   label: 'Payment Received',    icon: Wallet },
  { key: 'completed',          label: 'Completed',           icon: CheckCircle2 },
];

function TransactionTimeline({ stages_completed, current_stage }) {
  return (
    <div className="flex flex-col gap-0 mt-4">
      {STAGES.map((stage, i) => {
        const done = stages_completed?.includes(stage.key);
        const current = stage.key === current_stage;
        const Icon = stage.icon;

        return (
          <div key={stage.key} className="flex items-start gap-3">
            {/* Icon + connector line */}
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 flex-shrink-0 ${
                done ? 'bg-green-600 border-green-600 text-white'
                : current ? 'bg-green-100 border-green-600 text-green-600'
                : 'bg-white border-gray-200 text-gray-300'
              }`}>
                <Icon className="w-4 h-4" />
              </div>
              {i < STAGES.length - 1 && (
                <div className={`w-0.5 h-6 mt-1 ${done ? 'bg-green-400' : 'bg-gray-200'}`} />
              )}
            </div>

            {/* Label */}
            <div className="pb-4">
              <p className={`text-sm font-medium leading-relaxed ${
                done ? 'text-gray-900'
                : current ? 'text-green-700 font-semibold'
                : 'text-gray-400'
              }`}>
                {stage.label}
                {current && !done && (
                  <span className="ml-2 badge-yellow text-xs">Current</span>
                )}
                {done && stage.key !== current_stage && (
                  <span className="ml-2 text-xs text-green-500">✓</span>
                )}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function TransactionCard({ txn }) {
  const [showTimeline, setShowTimeline] = useState(false);

  return (
    <div className="card">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-mono text-xs text-gray-400">#{txn.id}</span>
            <StatusBadge status={txn.payment_status} />
          </div>
          <h3 className="font-bold text-gray-900">{txn.buyer}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{txn.crop} · {txn.quantity} quintals</p>
        </div>

        {/* Amount */}
        <div className="text-right">
          <p className="text-2xl font-bold text-green-800">
            ₹{txn.total_amount.toLocaleString('en-IN')}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">
            ₹{txn.agreed_price.toLocaleString('en-IN')}/qtl × {txn.quantity} qtl
          </p>
        </div>
      </div>

      {/* Stage summary */}
      <div className="bg-gray-50 rounded-xl p-3 mb-4">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-gray-700">
            Current stage: <span className="text-green-700 font-semibold capitalize">
              {txn.current_stage?.replace(/_/g, ' ')}
            </span>
          </p>
          <span className={`text-sm font-semibold ${
            txn.payment_status === 'received' ? 'text-green-600'
            : txn.payment_status === 'pending' ? 'text-amber-600'
            : 'text-gray-500'
          }`}>
            Payment: {txn.payment_status}
          </span>
        </div>

        {/* Simple progress bar */}
        <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full transition-all duration-500"
            style={{
              width: `${((txn.stages_completed?.length || 1) / STAGES.length) * 100}%`
            }}
          />
        </div>
        <p className="text-xs text-gray-400 mt-1">
          {txn.stages_completed?.length || 1} of {STAGES.length} stages complete
        </p>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 text-xs text-amber-700 mb-4">
        ⚠️ Demo Transaction — No real money is involved. This is for demonstration only.
      </div>

      {/* Timeline toggle */}
      <button
        onClick={() => setShowTimeline(!showTimeline)}
        className="text-green-700 text-sm font-semibold hover:underline"
      >
        {showTimeline ? 'Hide Timeline' : 'Show Full Timeline'}
      </button>

      {showTimeline && (
        <TransactionTimeline
          stages_completed={txn.stages_completed}
          current_stage={txn.current_stage}
        />
      )}
    </div>
  );
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const res = await getTransactions();
      if (res.success) setTransactions(res.data);
      setLoading(false);
    }
    load();
  }, []);

  const totalAmount = transactions.reduce((s, t) => s + t.total_amount, 0);
  const received = transactions.filter(t => t.payment_status === 'received');

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
        <p className="text-gray-500 text-sm mt-1">Track your sales from offer to payment</p>
      </div>

      {/* Summary */}
      {!loading && transactions.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <div className="card text-center p-4">
            <p className="text-2xl font-bold text-gray-900">{transactions.length}</p>
            <p className="text-sm text-gray-500 mt-0.5">Total</p>
          </div>
          <div className="card text-center p-4">
            <p className="text-2xl font-bold text-green-700">{received.length}</p>
            <p className="text-sm text-gray-500 mt-0.5">Paid</p>
          </div>
          <div className="card text-center p-4">
            <p className="text-lg font-bold text-gray-900">₹{(totalAmount / 100000).toFixed(1)}L</p>
            <p className="text-sm text-gray-500 mt-0.5">Total Value</p>
          </div>
        </div>
      )}

      {loading ? <LoadingState /> : transactions.length === 0 ? (
        <EmptyState
          title="No transactions yet"
          description="Accept a buyer offer to start a transaction."
        />
      ) : (
        <div className="space-y-4">
          {transactions.map(txn => (
            <TransactionCard key={txn.id} txn={txn} />
          ))}
        </div>
      )}
    </div>
  );
}
