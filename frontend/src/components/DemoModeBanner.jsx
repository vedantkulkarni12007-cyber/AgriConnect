// =============================================================
// Demo Mode Banner
// Shown only when explicit demo mode is active or user is previewing unauthenticated
// =============================================================

import { FlaskConical } from 'lucide-react';
import { isExplicitDemoMode } from '../services/api';

export default function DemoModeBanner() {
  const hasRealToken = !!localStorage.getItem('krishilink_access_token');
  const explicitDemo = isExplicitDemoMode();

  // If user is logged in with a real JWT account and not in explicit demo mode, hide banner
  if (hasRealToken && !explicitDemo) return null;

  return (
    <div className="bg-amber-50 border-b border-amber-200">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-2 text-amber-800 text-sm">
        <FlaskConical className="w-4 h-4 flex-shrink-0" />
        <span className="font-semibold">{explicitDemo ? 'Explicit Demo Mode' : 'Preview Mode'}</span>
        <span className="text-amber-700">
          — {explicitDemo
            ? 'Connected to local mock dataset for demonstration.'
            : 'You are previewing sample data. Register or log in to access live mandi data.'}
        </span>
      </div>
    </div>
  );
}
