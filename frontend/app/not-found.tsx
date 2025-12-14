import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center space-y-6">
        <h1 className="text-6xl font-bold text-white" style={{ color: "var(--color-primary-cyan)" }}>
          404
        </h1>
        <p className="text-xl text-gray-400">
          Quantum Signal Not Found
        </p>
        <Link
          href="/"
          className="px-6 py-3 rounded-lg text-white transition-colors"
          style={{
            backgroundColor: "rgba(0, 240, 255, 0.1)",
            borderColor: "rgba(0, 240, 255, 0.3)",
            color: "var(--color-primary-cyan)"
          }}
        >
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}