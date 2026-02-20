'use client';

import { useState } from 'react';

interface ForgeResult {
  status: string;
  forge_run_id: string;
  dry_run: boolean;
  elixir_path?: string;
  grade?: {
    total_score: number;
    soul_resonance: number;
    passed: boolean;
  };
  message: string;
  error?: string;
}

export function AlchemicalForgeButton() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ForgeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check for HiC authorization
  // In production, this would check against SOUL_KEY === "alchemist-approved" or hic_id === "russell"
  const isHiC = typeof window !== 'undefined' && (
    process.env.NEXT_PUBLIC_SOUL_KEY === 'alchemist-approved' ||
    localStorage.getItem('hic_id') === 'russell' ||
    true // For now, visible to all (can be restricted in production)
  );

  if (!isHiC) {
    return null;
  }

  const igniteForge = async (dryRun: boolean = true) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_BPRD_MEETINGS_URL || 'https://bprd-meetings.onrender.com';
      const apiKey = process.env.NEXT_PUBLIC_BPRD_API_KEY || '';

      const response = await fetch(`${apiUrl}/api/v1/ignite-the-forge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': apiKey,
        },
        body: JSON.stringify({ dry_run: dryRun, turns: 4 }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to ignite the forge');
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="glass-card rounded-2xl p-4 sm:p-6 relative overflow-hidden">
      {/* Glowing background effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-red-500/10 animate-pulse" />
      
      <div className="relative z-10">
        <h2 className="text-lg sm:text-xl font-bold mb-4 flex items-center gap-2">
          <span className="text-amber-400">🔮</span>
          Alchemical Forge
          <span className="text-xs font-normal text-muted-foreground ml-2">(HiC Only)</span>
        </h2>

        <p className="text-sm text-muted-foreground mb-4">
          Transmute the latest Jules Daily Brief into a fully expanded Elixir,
          verified by the Philosopher&apos;s Stone.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => igniteForge(true)}
            disabled={isLoading}
            className={`
              relative px-6 py-3 rounded-lg font-semibold text-sm
              bg-gradient-to-r from-amber-500 to-orange-500
              hover:from-amber-400 hover:to-orange-400
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-300
              shadow-lg shadow-amber-500/25
              hover:shadow-amber-500/40
              hover:scale-105
              ${isLoading ? 'animate-pulse' : ''}
            `}
            style={{
              animation: isLoading ? undefined : 'glow 2s ease-in-out infinite alternate',
            }}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Transmuting...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                🔥 Ignite the Alchemical Forge
                <span className="text-xs opacity-75">(Dry Run)</span>
              </span>
            )}
          </button>

          <button
            onClick={() => igniteForge(false)}
            disabled={isLoading}
            className={`
              px-6 py-3 rounded-lg font-semibold text-sm
              bg-gradient-to-r from-red-600 to-red-700
              hover:from-red-500 hover:to-red-600
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-300
              border border-red-400/30
            `}
          >
            🔥 Full Transmutation
          </button>
        </div>

        {/* Result display */}
        {result && (
          <div className={`mt-4 p-4 rounded-lg ${result.status === 'completed' ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
            <div className="flex items-center gap-2 mb-2">
              <span>{result.status === 'completed' ? '✨' : '❌'}</span>
              <span className="font-semibold">{result.message}</span>
            </div>
            {result.grade && (
              <div className="text-sm space-y-1">
                <p>Grade: <span className={result.grade.passed ? 'text-green-400' : 'text-amber-400'}>{result.grade.total_score}/100</span></p>
                <p>Soul Resonance: {result.grade.soul_resonance}/20</p>
                <p>Status: {result.grade.passed ? '✅ Passed' : '⚠️ Below threshold'}</p>
              </div>
            )}
            {result.elixir_path && (
              <p className="text-xs text-muted-foreground mt-2">
                Elixir: {result.elixir_path}
              </p>
            )}
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <p className="text-red-400">Error: {error}</p>
          </div>
        )}
      </div>

      {/* CSS for glow animation */}
      <style jsx>{`
        @keyframes glow {
          from {
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
          }
          to {
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.5), 0 0 60px rgba(245, 158, 11, 0.2);
          }
        }
      `}</style>
    </section>
  );
}
