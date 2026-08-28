// =============================================================
// Loading, Error, and Empty State Components
// Every page must show meaningful feedback — never blank screens
// =============================================================

import { Loader2, AlertCircle, SearchX, RefreshCw } from 'lucide-react';

// Loading spinner
export function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 className="w-10 h-10 text-green-600 animate-spin" />
      <p className="text-gray-500 font-medium">{message}</p>
    </div>
  );
}

// Error state with retry button
export function ErrorState({ message = 'Something went wrong. Please try again.', onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      <div className="w-14 h-14 bg-red-50 rounded-full flex items-center justify-center">
        <AlertCircle className="w-8 h-8 text-red-500" />
      </div>
      <div>
        <p className="text-gray-700 font-semibold mb-1">Unable to Load Data</p>
        <p className="text-gray-500 text-sm max-w-sm">{message}</p>
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
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-center">
      <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center">
        <SearchX className="w-8 h-8 text-gray-400" />
      </div>
      <div>
        <p className="text-gray-700 font-semibold mb-1">{title}</p>
        {description && <p className="text-gray-500 text-sm max-w-sm">{description}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

// Page-level loading for first render
export function PageLoader() {
  return (
    <div className="min-h-screen bg-[#FAFAF7] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 bg-green-800 rounded-xl flex items-center justify-center animate-pulse">
          <span className="text-white text-xl">🌿</span>
        </div>
        <p className="text-green-800 font-semibold">KrishiLink</p>
        <Loader2 className="w-6 h-6 text-green-600 animate-spin" />
      </div>
    </div>
  );
}
