import { Target, CheckCircle2, Circle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import fs from 'fs';
import path from 'path';

interface InvestigationMetrics {
  phases: Array<{
    number: number;
    name: string;
    status: string;
  }>;
  componentsComplete: number;
  totalComponents: number;
  successCriteria: Array<{
    name: string;
    current: number;
    target: string;
    complete: boolean;
  }>;
  overallProgress: number;
}

export function InvestigationProgress() {
  // Read production data
  let investigationMetrics: InvestigationMetrics | null = null;

  try {
    const dataPath = path.join(process.cwd(), 'src/content/production.json');
    if (fs.existsSync(dataPath)) {
      const fileContent = fs.readFileSync(dataPath, 'utf-8');
      const data = JSON.parse(fileContent);
      investigationMetrics = data.investigationMetrics;
    }
  } catch (error) {
    console.error('Error reading investigation metrics:', error);
  }

  if (!investigationMetrics || investigationMetrics.phases.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Target className="w-10 h-10 mx-auto mb-3 opacity-50" />
        <p className="text-sm">Investigation data not available</p>
      </div>
    );
  }

  const getStatusBadgeVariant = (status: string) => {
    if (status.toUpperCase().includes('COMPLETE')) return 'default';
    if (status.toUpperCase().includes('PROGRESS')) return 'secondary';
    return 'outline';
  };

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Overall Progress
          </h3>
          <span className="text-2xl font-black text-primary neon-pulse">
            {investigationMetrics.overallProgress}%
          </span>
        </div>
        <Progress value={investigationMetrics.overallProgress} className="h-3" />
        <p className="text-xs text-muted-foreground mt-2">
          {investigationMetrics.componentsComplete} of{' '}
          {investigationMetrics.totalComponents} components complete
        </p>
      </div>

      {/* Phases */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Phase Status
        </h3>
        <div className="space-y-3">
          {investigationMetrics.phases.map((phase) => (
            <div
              key={phase.number}
              className="flex items-center justify-between p-3 rounded-lg bg-secondary/30"
            >
              <div className="flex items-center gap-3">
                {phase.status.toUpperCase().includes('COMPLETE') ? (
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                ) : (
                  <Circle className="w-4 h-4 text-muted-foreground" />
                )}
                <div>
                  <p className="text-sm font-medium">Phase {phase.number}</p>
                  <p className="text-xs text-muted-foreground">{phase.name}</p>
                </div>
              </div>
              <Badge variant={getStatusBadgeVariant(phase.status)} className="text-xs">
                {phase.status}
              </Badge>
            </div>
          ))}
        </div>
      </div>

      {/* Success Criteria */}
      {investigationMetrics.successCriteria.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Success Criteria
          </h3>
          <div className="space-y-2">
            {investigationMetrics.successCriteria.map((criteria, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{criteria.name}</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-semibold">
                    {criteria.current} / {criteria.target}
                  </span>
                  {criteria.complete && (
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Project Link */}
      <div className="pt-4 border-t border-border/50">
        <a
          href="/research/corruption-investigation"
          className="text-sm text-primary hover:underline flex items-center gap-2"
        >
          <Target className="w-4 h-4" />
          View Full Investigation Details →
        </a>
      </div>
    </div>
  );
}
