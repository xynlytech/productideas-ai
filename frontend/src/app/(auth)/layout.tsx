export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-deepest">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-accent-blue/8 rounded-full blur-[120px]" />
      </div>
      <div className="relative w-full max-w-md mx-auto px-6">{children}</div>
    </div>
  );
}
