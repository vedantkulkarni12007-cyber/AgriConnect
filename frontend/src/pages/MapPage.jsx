// =============================================================
// Map Page
// Interactive map with mandis, buyers, and storage markers
// Uses React Leaflet + OpenStreetMap (no API key required!)
// =============================================================

import { useState, useEffect } from 'react';
import { MapPin, Warehouse, ShoppingBag, Store } from 'lucide-react';
import { DEMO_MARKERS } from '../data/demoData';

// We load Leaflet dynamically to avoid SSR issues
// (Leaflet needs browser window to render)
let MapContainer, TileLayer, Marker, Popup, L;

const FILTERS = [
  { value: 'all', label: 'All', icon: MapPin },
  { value: 'mandi', label: 'Mandis', icon: Store },
  { value: 'buyer', label: 'Buyers', icon: ShoppingBag },
  { value: 'storage', label: 'Storage', icon: Warehouse },
];

// Color-coded marker icons by type
function getMarkerColor(type) {
  return type === 'mandi' ? '#2D6A4F'
    : type === 'buyer' ? '#2563EB'
    : '#D97706';
}

// SVG pin icon
function createIcon(color) {
  if (!L) return null;
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="24" height="36">
      <path d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24C24 5.4 18.6 0 12 0z"
        fill="${color}" stroke="white" stroke-width="1.5"/>
      <circle cx="12" cy="12" r="4" fill="white"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    iconSize: [24, 36],
    iconAnchor: [12, 36],
    popupAnchor: [0, -36],
    className: '',
  });
}

function LeafletMap({ markers }) {
  useEffect(() => {
    // Fix leaflet default icon
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    });
  }, []);

  return (
    <MapContainer
      center={[20.0, 73.8]}
      zoom={8}
      style={{ height: '100%', width: '100%' }}
      className="rounded-2xl"
    >
      <TileLayer
        attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map(marker => (
        <Marker
          key={marker.id}
          position={[marker.lat, marker.lng]}
          icon={createIcon(getMarkerColor(marker.type))}
        >
          <Popup>
            <div className="p-1 min-w-40">
              <div className="flex items-center gap-1.5 mb-1">
                <span className={`w-2.5 h-2.5 rounded-full inline-block`} style={{ background: getMarkerColor(marker.type) }} />
                <span className="text-xs font-semibold text-gray-500 capitalize">{marker.type}</span>
              </div>
              <p className="font-bold text-gray-900 text-sm">{marker.name}</p>
              <p className="text-xs text-gray-600 mt-1">{marker.info}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default function MapPage() {
  const [filter, setFilter] = useState('all');
  const [mapReady, setMapReady] = useState(false);
  const [mapError, setMapError] = useState(false);

  // Dynamically import Leaflet (required for browser-only library)
  useEffect(() => {
    async function loadLeaflet() {
      try {
        const leaflet = await import('leaflet');
        const reactLeaflet = await import('react-leaflet');
        L = leaflet.default;
        MapContainer = reactLeaflet.MapContainer;
        TileLayer = reactLeaflet.TileLayer;
        Marker = reactLeaflet.Marker;
        Popup = reactLeaflet.Popup;
        // Load CSS
        if (!document.querySelector('link[href*="leaflet"]')) {
          const link = document.createElement('link');
          link.rel = 'stylesheet';
          link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
          document.head.appendChild(link);
        }
        setMapReady(true);
      } catch (e) {
        setMapError(true);
      }
    }
    loadLeaflet();
  }, []);

  const filtered = filter === 'all' ? DEMO_MARKERS : DEMO_MARKERS.filter(m => m.type === filter);

  const counts = {
    mandi: DEMO_MARKERS.filter(m => m.type === 'mandi').length,
    buyer: DEMO_MARKERS.filter(m => m.type === 'buyer').length,
    storage: DEMO_MARKERS.filter(m => m.type === 'storage').length,
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="mb-6 flex-shrink-0">
        <p className="section-label">Interactive Locator</p>
        <h1 className="text-2xl font-bold text-gray-900">Market Map</h1>
        <p className="text-gray-500 text-sm mt-1">
          Find mandis, buyers, and storage facilities near you
        </p>
      </div>

      <div className="flex-1 grid lg:grid-cols-4 gap-6 min-h-0">
        {/* LEFT: Map */}
        <div className="lg:col-span-3 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col relative z-0">
          {/* Floating Legend */}
          <div className="absolute top-4 right-4 z-[400] bg-white/90 backdrop-blur-sm px-4 py-3 rounded-xl shadow-md border border-gray-100 flex flex-col gap-2 pointer-events-auto">
            <p className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-1">Legend</p>
            <span className="flex items-center gap-2 text-xs font-medium text-gray-600">
              <span className="w-3 h-3 rounded-full bg-green-800 inline-block shadow-sm" />Mandi ({counts.mandi})
            </span>
            <span className="flex items-center gap-2 text-xs font-medium text-gray-600">
              <span className="w-3 h-3 rounded-full bg-blue-600 inline-block shadow-sm" />Buyer ({counts.buyer})
            </span>
            <span className="flex items-center gap-2 text-xs font-medium text-gray-600">
              <span className="w-3 h-3 rounded-full bg-amber-500 inline-block shadow-sm" />Storage ({counts.storage})
            </span>
          </div>

          {mapError ? (
            <div className="h-full flex flex-col items-center justify-center gap-4 text-center px-4 bg-gray-50">
              <MapPin className="w-12 h-12 text-gray-300" />
              <div>
                <p className="font-semibold text-gray-700">Map could not load</p>
                <p className="text-sm text-gray-500 mt-1 max-w-sm">
                  Make sure you are connected to the internet. The map uses OpenStreetMap tiles.
                </p>
              </div>
            </div>
          ) : !mapReady ? (
            <div className="h-full flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                <p className="text-gray-500 text-sm font-medium">Loading interactive map...</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 w-full h-full relative z-0">
              <LeafletMap markers={filtered} />
            </div>
          )}
          <div className="bg-gray-50 p-2 text-center border-t border-gray-100 z-10">
            <p className="text-[10px] text-gray-400">
              Map data © OpenStreetMap contributors. Marker locations are approximate demo data.
            </p>
          </div>
        </div>

        {/* RIGHT: Filters + List */}
        <div className="lg:col-span-1 flex flex-col gap-4 overflow-hidden">
          {/* Filters */}
          <div className="card p-4 flex-shrink-0">
            <p className="text-sm font-bold text-gray-900 mb-3">Filter Points</p>
            <div className="flex flex-col gap-2">
              {FILTERS.map(f => {
                const Icon = f.icon;
                return (
                  <button
                    key={f.value}
                    onClick={() => setFilter(f.value)}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all w-full text-left ${
                      filter === f.value
                        ? 'bg-green-800 text-white shadow-sm'
                        : 'bg-white border border-gray-200 text-gray-600 hover:border-green-300 hover:bg-green-50/50'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <Icon className="w-4 h-4" />
                      {f.label}
                    </span>
                    {f.value !== 'all' && (
                      <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                        filter === f.value ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-500'
                      }`}>
                        {counts[f.value] || 0}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* List */}
          <div className="card flex-1 overflow-y-auto p-0">
            <div className="p-4 border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur-sm z-10">
              <h2 className="font-bold text-gray-900">Locations</h2>
              <p className="text-xs text-gray-500 mt-0.5">Showing {filtered.length} points</p>
            </div>
            <div className="divide-y divide-gray-50">
              {filtered.map(marker => (
                <div key={marker.id} className="p-4 hover:bg-green-50/30 transition-colors">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-sm"
                      style={{ background: getMarkerColor(marker.type) }}
                    />
                    <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">{marker.type}</span>
                  </div>
                  <p className="font-semibold text-gray-800 text-sm">{marker.name}</p>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed line-clamp-2">{marker.info}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
