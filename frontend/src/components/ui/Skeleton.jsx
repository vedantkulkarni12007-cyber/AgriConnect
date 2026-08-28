export function Skeleton({ className="" }) {
  return <div className={`animate-pulse rounded bg-gray-200 ${className}`} />;
}
export function EmptyState({ title="No data", description, action }) {
  return <div className="text-center py-12"><p className="font-medium">{title}</p>{description && <p className="text-sm text-gray-500">{description}</p>}{action}</div>;
}
export function ErrorState({ message="Something went wrong", retry }) {
  return <div className="text-center py-12 text-red-600"><p>{message}</p>{retry && <button onClick={retry} className="text-sm underline">Retry</button>}</div>;
}
