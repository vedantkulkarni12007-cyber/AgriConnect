// =============================================================
// Demo Mode Banner
// Shown on every page to indicate this is demo data
// =============================================================

import { FlaskConical, Info } from 'lucide-react';

export default function DemoModeBanner() {
  return (
    <div className="bg-amber-50 border-b border-amber-200">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-2 text-amber-800 text-sm">
        <FlaskConical className="w-4 h-4 flex-shrink-0" />
        <span className="font-semibold">Demo Mode</span>
        <span className="text-amber-700">
          — You are viewing realistic sample data. No account or API needed.
        </span>
      </div>
    </div>
  );
}
