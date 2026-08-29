// =============================================================
// Demo Mode Banner
// Only shown when the user is NOT logged in with a real account
// (i.e. no JWT access token stored — using demo/local session)
// =============================================================

import { FlaskConical } from 'lucide-react';

export default function DemoModeBanner() {
  // If there's a real JWT access token the user registered via API — don't show demo banner
  const hasRealToken = !!localStorage.getItem('krishilink_access_token');
  if (hasRealToken) return null;

  return (
    <div className="bg-amber-50 border-b border-amber-200">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-2 text-amber-800 text-sm">
        <FlaskConical className="w-4 h-4 flex-shrink-0" />
        <span className="font-semibold">Demo Mode</span>
        <span className="text-amber-700">
          — You are viewing sample data. Register or login to use live data.
        </span>
      </div>
    </div>
  );
}
