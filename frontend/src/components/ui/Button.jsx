export function Button({ variant="default", size="md", className="", children, ...props }) {
  const base="inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none disabled:opacity-50";
  const variants={default:"bg-green-600 text-white hover:bg-green-700", outline:"border border-green-600 text-green-700 hover:bg-green-50", ghost:"hover:bg-gray-100"};
  const sizes={md:"h-9 px-4 py-2", sm:"h-8 px-3 text-sm", lg:"h-10 px-6"};
  return <button className={`${base} ${variants[variant]||variants.default} ${sizes[size]||sizes.md} ${className}`} {...props}>{children}</button>;
}
