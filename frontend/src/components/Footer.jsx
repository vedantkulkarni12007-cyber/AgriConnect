// =============================================================
// Footer Component
// =============================================================

import { Link } from 'react-router-dom';
import { Sprout, GitBranch, Mail } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-green-900 text-white">
      <div className="max-w-7xl mx-auto px-4 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 bg-white/20 rounded-xl flex items-center justify-center">
                <Sprout className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">KrishiLink</span>
            </div>

            <p className="text-green-200 text-sm leading-relaxed">
              Better Prices. Better Buyers. Better Decisions.
            </p>

            <p className="text-green-300 text-xs mt-3">
              Smart India Hackathon 2026 Project
            </p>
          </div>

          {/* Features */}
          <div>
            <h4 className="font-semibold mb-3 text-green-100">Features</h4>

            <ul className="space-y-2 text-sm text-green-300">
              <li>
                <Link
                  to="/prices"
                  className="hover:text-white transition-colors"
                >
                  Market Prices
                </Link>
              </li>

              <li>
                <Link
                  to="/sell"
                  className="hover:text-white transition-colors"
                >
                  Sell Produce
                </Link>
              </li>

              <li>
                <Link
                  to="/matches"
                  className="hover:text-white transition-colors"
                >
                  Buyer Matching
                </Link>
              </li>

              <li>
                <Link
                  to="/map"
                  className="hover:text-white transition-colors"
                >
                  Market Map
                </Link>
              </li>

              <li>
                <Link
                  to="/transactions"
                  className="hover:text-white transition-colors"
                >
                  Transactions
                </Link>
              </li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h4 className="font-semibold mb-3 text-green-100">About</h4>

            <ul className="space-y-2 text-sm text-green-300">
              <li>
                <a
                  href="#how-it-works"
                  className="hover:text-white transition-colors"
                >
                  How It Works
                </a>
              </li>

              <li>
                <a
                  href="#"
                  className="hover:text-white transition-colors"
                >
                  For Farmers
                </a>
              </li>

              <li>
                <a
                  href="#"
                  className="hover:text-white transition-colors"
                >
                  For Buyers
                </a>
              </li>

              <li>
                <a
                  href="#"
                  className="hover:text-white transition-colors"
                >
                  For FPOs
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-3 text-green-100">Contact</h4>

            <div className="flex items-center gap-2 text-sm text-green-300 mb-2">
              <Mail className="w-4 h-4" />
              <span>team@krishilink.in</span>
            </div>

            <div className="flex items-center gap-2 text-sm text-green-300">
              <GitBranch className="w-4 h-4" />
              <span>github.com/krishilink</span>
            </div>
          </div>
        </div>

        <div className="border-t border-green-800 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-green-400">
          <p>© 2026 Krishi Link. Built for Smart India Hackathon.</p>

          <p className="text-xs">
            Running in Demo Mode — Prices are sample data for demonstration
            only.
          </p>
        </div>
      </div>
    </footer>
  );
}