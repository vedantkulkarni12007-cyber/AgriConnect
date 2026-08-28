export function Badge({ variant="default", className="", children, ...props }) {
  const v={default:"bg-green-100 text-green-800", verified:"bg-blue-100 text-blue-800", warning:"bg-amber-100 text-amber-800", error:"bg-red-100 text-red-800"};
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${v[variant]||v.default} ${className}`} {...props}>{children}</span>;
}
export function VerificationBadge({ verified }) {
  return <Badge variant={verified ? "verified" : "warning"}>{verified ? "Verified" : "Unverified"}</Badge>;
}
export function TrendBadge({ trend }) {
  const m={RISING:"warning", FALLING:"error", STABLE:"default", VOLATILE:"error"};
  return <Badge variant={m[trend]||"default"}>{trend}</Badge>;
}
export function DataQualityBadge({ quality }) {
  const m={HIGH:"verified", MEDIUM:"default", LOW:"warning"};
  return <Badge variant={m[quality]||"default"}>Data: {quality}</Badge>;
}
