'use client';

import { useEffect, useState } from 'react';
import { getMonthlyUsage } from '@/app/actions/get-usage';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Activity } from 'lucide-react';

interface UsageData {
  month: string;
  spent_usd: number;
  budget_cap_usd: number;
  budget_alert_usd: number;
  budget_remaining_usd: number;
  breakdown: Record<string, number>;
  status: 'ok' | 'alert' | 'over_cap';
}

export default function ApiUsageMonitor() {
  const [data, setData] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const res = await getMonthlyUsage();
        if (res.success) {
          setData(res.data);
          setError(null);
        } else {
          setError(res.message || 'Unknown error');
        }
      } catch (err) {
        setError('Failed to load usage data.');
      } finally {
        setLoading(false);
      }
    };

    fetchUsage();
    // Poll every 30 seconds
    const interval = setInterval(fetchUsage, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
      <Card className="border-primary/20 bg-black/40 backdrop-blur-xl animate-pulse">
          <CardContent className="p-4">
              <div className="h-4 bg-primary/20 rounded w-1/2 mb-2"></div>
              <div className="h-2 bg-muted rounded w-full"></div>
          </CardContent>
      </Card>
  );

  if (error) return (
      <Card className="border-red-500/20 bg-red-950/20 backdrop-blur-xl">
          <CardContent className="p-4 text-xs text-red-400">
              Error loading usage: {error}
          </CardContent>
      </Card>
  );

  if (!data) return null;

  const percentage = Math.min((data.spent_usd / data.budget_cap_usd) * 100, 100);
  const isAlert = data.status !== 'ok';

  // Color logic for Progress bar
  let statusColor = '[&>div]:bg-primary';
  if (percentage > 75) statusColor = '[&>div]:bg-yellow-500';
  if (percentage >= 90) statusColor = '[&>div]:bg-red-500';
  if (data.status === 'over_cap') statusColor = '[&>div]:bg-red-600';

  return (
    <Card className="border-primary/20 bg-black/40 backdrop-blur-xl shadow-lg shadow-primary/5">
      <CardHeader className="py-3 pb-2 border-b border-white/5">
        <div className="flex justify-between items-center">
             <CardTitle className="text-sm font-medium uppercase tracking-wider flex items-center gap-2 text-muted-foreground">
                <Activity className="w-4 h-4 text-primary" />
                API Budget Monitor
             </CardTitle>
             <Badge variant={isAlert ? 'destructive' : 'outline'} className="font-mono text-[10px] h-5">
                {data.status === 'over_cap' ? 'CAP REACHED' : data.status.toUpperCase()}
             </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-4">
        {/* Total Progress */}
        <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
                <span className="text-muted-foreground">Total Monthly Spend</span>
                <span className={isAlert ? 'text-red-400 font-bold' : 'text-primary'}>
                    ${data.spent_usd.toFixed(2)} / ${data.budget_cap_usd.toFixed(2)}
                </span>
            </div>
            <Progress value={percentage} className={`h-2 ${statusColor}`} />
            <div className="flex justify-between text-[10px] text-muted-foreground uppercase font-mono">
                <span>Month: {data.month}</span>
                <span className={data.budget_remaining_usd < 5 ? 'text-red-400 font-bold' : 'text-green-400'}>
                    ${data.budget_remaining_usd.toFixed(2)} Remaining
                </span>
            </div>
        </div>

        {/* Breakdown */}
        {data.breakdown && (
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5">
                {Object.entries(data.breakdown).map(([agent, cost]) => {
                    // Always show requested agents even if 0? No, show what we have.
                    return (
                        <div key={agent} className="flex items-center justify-between p-2 rounded bg-muted/20 border border-white/5">
                            <div className="flex items-center gap-2">
                                <div className={`w-1.5 h-1.5 rounded-full ${cost > 0 ? 'bg-green-400' : 'bg-gray-600'}`}></div>
                                <span className="capitalize text-[10px] font-bold text-muted-foreground">{agent}</span>
                            </div>
                            <span className="font-mono text-[10px] text-primary">${cost.toFixed(3)}</span>
                        </div>
                    );
                })}
            </div>
        )}

        {isAlert && (
            <div className="flex items-center gap-2 p-2 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-xs animate-pulse">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>Warning: Budget limit approaching!</span>
            </div>
        )}
      </CardContent>
    </Card>
  );
}
