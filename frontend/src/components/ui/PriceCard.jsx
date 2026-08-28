import { Card, CardHeader, CardContent } from "./Card.jsx";
import { TrendBadge, DataQualityBadge } from "./Badge.jsx";
export function PriceCard({ crop, market, modal, min, max, trend, quality, volume, onExplain }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row justify-between items-center">
        <div><div className="font-semibold">{crop} — {market}</div><div className="text-xs text-gray-500">{volume} tonnes</div></div>
        <TrendBadge trend={trend} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">₹{modal}<span className="text-sm font-normal">/quintal</span></div>
        <div className="text-sm text-gray-600">₹{min} — ₹{max} <DataQualityBadge quality={quality || "MEDIUM"} /></div>
        {onExplain && <button onClick={onExplain} className="text-xs text-green-600 mt-2">How calculated?</button>}
      </CardContent>
    </Card>
  );
}
