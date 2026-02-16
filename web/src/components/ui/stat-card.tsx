'use client';

import { useEffect, useState } from 'react';
import { LucideIcon } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface StatCardProps {
  label: string;
  value: number;
  trend?: 'up' | 'down' | 'neutral';
  icon?: LucideIcon;
  suffix?: string;
  className?: string;
}

export function StatCard({
  label,
  value,
  trend = 'neutral',
  icon: Icon,
  suffix = '',
  className = '',
}: StatCardProps) {
  const [count, setCount] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    setIsAnimating(true);
    const duration = 1500; // Animation duration in ms
    const steps = 60; // Number of animation steps
    const increment = value / steps;
    const stepDuration = duration / steps;

    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        setIsAnimating(false);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [value]);

  const trendColors = {
    up: 'text-green-400',
    down: 'text-red-400',
    neutral: 'text-muted-foreground',
  };

  const trendIcons = {
    up: '↑',
    down: '↓',
    neutral: '→',
  };

  return (
    <Card className={`glass-card relative overflow-hidden ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent" />

      <CardContent className="p-6 relative z-10">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
              {label}
            </p>
            <div className="flex items-baseline gap-2">
              <p
                className={`text-4xl font-black ${
                  isAnimating ? 'text-primary' : ''
                }`}
              >
                {count}
                {suffix}
              </p>
              {trend !== 'neutral' && (
                <span className={`text-sm font-semibold ${trendColors[trend]}`}>
                  {trendIcons[trend]}
                </span>
              )}
            </div>
          </div>

          {Icon && (
            <div className="p-3 rounded-xl bg-primary/10 text-primary">
              <Icon className="w-6 h-6" />
            </div>
          )}
        </div>

        {/* Progress ring visualization */}
        <div className="mt-4">
          <div className="h-1 bg-secondary/30 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-1000 ease-out"
              style={{ width: isAnimating ? `${(count / value) * 100}%` : '100%' }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
