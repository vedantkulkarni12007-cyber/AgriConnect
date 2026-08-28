// =============================================================
// Loading, Error, and Empty State Components
// Every page must show meaningful feedback — never blank screens
// =============================================================

import { AlertCircle, RefreshCw, Leaf } from 'lucide-react';

// Loading spinner — agricultural pulse animation
export function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-5">
      {/* Layered animation: outer ring + leaf */}
      <div className="relative">
        <div className="w-14 h-14 rounded-full border-4 border-green-100 border-t-green-600 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Leaf className="w-5 h-5 text-green-600" />
        </div>
      </div>
      <div className="text-center">
        <p className="text-gray-700 font-semibold">{message}</p>
        <p className="text-xs text-gray-400 mt-1">Fetching latest data...</p>
      </div>
    </div>
  );
}

// Error state with retry button
export function ErrorState({ message = 'Something went wrong. Please try again.', onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-5 text-center">
      <div className="w-16 h-16 bg-red-50 rounded-2xl flex items-center justify-center border border-red-100">
        <AlertCircle className="w-8 h-8 text-red-500" />
      </div>
      <div>
        <p className="text-gray-800 font-bold text-lg mb-1">Unable to Load Data</p>
        <p className="text-gray-500 text-sm max-w-sm leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary btn-sm flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Try Again
        </button>
      )}
    </div>
  );
}

// Empty state (no data found)
export function EmptyState({ title = 'No data found', description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-5 text-center">
      <div className="w-20 h-20 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl flex items-center justify-center border border-green-200 shadow-sm">
        <div className="relative">
          <div className="w-10 h-10 bg-green-200/60 rounded-xl flex items-center justify-center">
            <Leaf className="w-6 h-6 text-green-700 rotate-12" />
          </div>
          <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-400 rounded-full" />
          <div className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-green-300 rounded-full" />
        </div>
      </div>
      <div>
        <p className="text-gray-800 font-bold text-base mb-1">{title}</p>
        {description && (
          <p className="text-gray-500 text-sm max-w-xs leading-relaxed">{description}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

// Page-level loading for first render
export function PageLoader() {
  return (
    <div className="min-h-screen bg-[#FAFAF7] flex items-center justify-center">
      <div className="flex flex-col items-center gap-5">
        <div className="relative">
          <div className="w-14 h-14 bg-green-800 rounded-2xl flex items-center justify-center shadow-lg">
            <Leaf className="w-7 h-7 text-white" />
          </div>
          <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-amber-400 rounded-full border-2 border-white flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          </div>
        </div>
        <div className="text-center">
          <p className="text-green-800 font-bold text-lg">KrishiLink</p>
          <p className="text-gray-400 text-xs mt-0.5">India's Agricultural Marketplace</p>
        </div>
        <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
      </div>
    </div>
  );
}

