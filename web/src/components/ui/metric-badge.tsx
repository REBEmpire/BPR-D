'use client';

import { Badge } from '@/components/ui/badge';

interface MetricBadgeProps {
  label: string;
  value: number | string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function MetricBadge({
  label,
  value,
  trend,
  className = '',
}: MetricBadgeProps) {
  const trendIndicators = {
    up: { symbol: '↑', color: 'text-green-400' },
    down: { symbol: '↓', color: 'text-red-400' },
    neutral: { symbol: '→', color: 'text-muted-foreground' },
  };

  const trendInfo = trend ? trendIndicators[trend] : null;

  return (
    <div className={`flex items-center justify-between py-2 ${className}`}>
      <span className="text-sm text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <Badge
          variant="outline"
          className="neon-pulse bg-primary/10 text-primary border-primary/30 font-mono font-bold"
        >
          {value}
        </Badge>
        {trendInfo && (
          <span className={`text-sm font-bold ${trendInfo.color}`}>
            {trendInfo.symbol}
          </span>
        )}
      </div>
    </div>
  );
}
