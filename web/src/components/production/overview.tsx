import { Users, FileText, Target, CheckCircle2 } from 'lucide-react';
import { StatCard } from '@/components/ui/stat-card';
import fs from 'fs';
import path from 'path';

interface ProductionData {
  meetings: any[];
  researchMetrics: {
    totalBriefs: number;
  };
  investigationMetrics: {
    overallProgress: number;
  };
  teamState: {
    activeProjects: any[];
  };
}

export function ProductionOverview() {
  // Read production data
  let productionData: ProductionData | null = null;

  try {
    const dataPath = path.join(process.cwd(), 'src/content/production.json');
    if (fs.existsSync(dataPath)) {
      const fileContent = fs.readFileSync(dataPath, 'utf-8');
      productionData = JSON.parse(fileContent);
    }
  } catch (error) {
    console.error('Error reading production data:', error);
  }

  // Default values if data not available
  const meetingsCount = productionData?.meetings.length || 0;
  const briefsCount = productionData?.researchMetrics.totalBriefs || 0;
  const investigationProgress = productionData?.investigationMetrics.overallProgress || 0;
  const projectsCount = productionData?.teamState.activeProjects.length || 0;

  // Calculate action items count from meetings
  const actionItemsCount =
    productionData?.meetings.reduce(
      (sum, meeting) => sum + (meeting.actionItemsCount || 0),
      0
    ) || 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        label="Team Meetings"
        value={meetingsCount}
        trend={meetingsCount > 0 ? 'up' : 'neutral'}
        icon={Users}
      />

      <StatCard
        label="Research Briefs"
        value={briefsCount}
        trend={briefsCount > 0 ? 'up' : 'neutral'}
        icon={FileText}
      />

      <StatCard
        label="Action Items"
        value={actionItemsCount}
        trend={actionItemsCount > 0 ? 'up' : 'neutral'}
        icon={CheckCircle2}
      />

      <StatCard
        label="Investigation"
        value={investigationProgress}
        suffix="%"
        trend={investigationProgress > 0 ? 'up' : 'neutral'}
        icon={Target}
      />
    </div>
  );
}
