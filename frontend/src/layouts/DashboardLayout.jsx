// =============================================================
// Dashboard Layout
// Used by: Farmer dashboard, Buyer dashboard, FPO dashboard
// Shows: Sidebar (desktop) + Top bar + Demo Banner + Page content
// =============================================================

import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, IndianRupee, ShoppingCart, Users,
  FileText, AlertTriangle, Map, Menu, X, Sprout,
  TrendingUp, Bell, LogOut, ChevronRight
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useLanguage } from '../hooks/useLanguage';
import DemoModeBanner from '../components/DemoModeBanner';
import { DEMO_NOTIFICATIONS } from '../data/demoData';

const farmerNav = [
  { label: 'Dashboard',    href: '/farmer/dashboard', icon: LayoutDashboard },
  { label: 'Market Prices',href: '/prices',            icon: IndianRupee },
  { label: 'Sell Produce', href: '/sell',              icon: ShoppingCart },
  { label: 'Buyer Matches',href: '/matches',           icon: Users },
  { label: 'Offers',       href: '/offers',            icon: FileText },
  { label: 'Transactions', href: '/transactions',      icon: TrendingUp },
  { label: 'Grievances',   href: '/grievances',        icon: AlertTriangle },
  { label: 'Market Map',   href: '/map',               icon: Map },
];

const buyerNav = [
  { label: 'Dashboard',    href: '/buyer/dashboard',  icon: LayoutDashboard },
  { label: 'Browse Lots',  href: '/offers',           icon: ShoppingCart },
  { label: 'My Offers',    href: '/offers',           icon: FileText },
  { label: 'Transactions', href: '/transactions',     icon: TrendingUp },
  { label: 'Market Map',   href: '/map',              icon: Map },
];

const fpoNav = [
  { label: 'Dashboard',    href: '/fpo/dashboard',    icon: LayoutDashboard },
  { label: 'Market Prices',href: '/prices',           icon: IndianRupee },
  { label: 'Sell Produce', href: '/sell',             icon: ShoppingCart },
  { label: 'Buyer Matches',href: '/matches',          icon: Users },
  { label: 'Offers',       href: '/offers',           icon: FileText },
  { label: 'Transactions', href: '/transactions',     icon: TrendingUp },
  { label: 'Market Map',   href: '/map',              icon: Map },
];

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = user?.role === 'buyer' ? buyerNav
    : user?.role === 'fpo' ? fpoNav
    : farmerNav;

  const unreadCount = DEMO_NOTIFICATIONS.filter(n => !n.is_read).length;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const Sidebar = ({ mobile = false }) => (
    <div className={`flex flex-col h-full ${mobile ? 'w-full' : 'w-64'}`}>
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 py-5 border-b border-green-700">
        <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
          <Sprout className="w-5 h-5 text-white" />
        </div>
        <span className="text-white font-bold text-lg">KrishiLink</span>
      </div>

      {/* User info */}
      <div className="px-4 py-4 border-b border-green-700">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">
              {user?.name?.[0] || 'U'}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-white font-semibold text-sm truncate">{user?.name}</p>
            <p className="text-green-200 text-xs capitalize">{user?.role}</p>
          </div>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.href + item.label}
              to={item.href}
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-white text-green-800 shadow-sm'
                  : 'text-green-100 hover:bg-white/10'
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {item.label}
              {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
            </Link>
          );
        })}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t border-green-700">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-green-100 hover:bg-white/10 text-sm font-medium transition-all"
        >
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#FAFAF7] flex">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex flex-col w-64 bg-green-800 fixed top-0 left-0 h-screen z-30">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div className={`fixed top-0 left-0 h-screen w-72 bg-green-800 z-50 transition-transform duration-300 lg:hidden ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <Sidebar mobile />
      </div>

      {/* Main content area */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-20">
          <div className="flex items-center justify-between px-4 py-3">
            {/* Mobile menu toggle */}
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>

            {/* Page breadcrumb */}
            <div className="hidden lg:block">
              <p className="text-sm text-gray-500">
                Welcome back, <span className="font-semibold text-gray-800">{user?.name?.split(' ')[0]}</span>
              </p>
            </div>

            {/* Right: Notifications */}
            <div className="relative ml-auto">
              <button
                onClick={() => setNotifOpen(!notifOpen)}
                className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <Bell className="w-5 h-5 text-gray-600" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notification dropdown */}
              {notifOpen && (
                <div className="absolute right-0 top-12 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden">
                  <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                    <span className="font-semibold text-gray-800">Notifications</span>
                    <span className="badge-yellow">{unreadCount} new</span>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {DEMO_NOTIFICATIONS.map(n => (
                      <div key={n.id} className={`px-4 py-3 border-b border-gray-50 hover:bg-gray-50 ${!n.is_read ? 'bg-green-50/50' : ''}`}>
                        <p className="font-semibold text-sm text-gray-800">{n.title}</p>
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                      </div>
                    ))}
                  </div>
                  <div className="px-4 py-3 text-center">
                    <span className="text-xs text-gray-400">Demo notifications — no real alerts</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Demo Banner */}
        <DemoModeBanner />

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-6 xl:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
