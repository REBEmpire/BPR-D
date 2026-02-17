import { Users, FileText, Target, CheckCircle2 } from 'lucide-react';
import { StatCard } from '@/components/ui/stat-card';
import fs from 'fs';
import path from 'path';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface ProductionData {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  meetings: any[];
  researchMetrics: {
    totalBriefs: number;
  };
  investigationMetrics: {
    overallProgress: number;
  };
  teamState: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
  // projectsCount is available if needed
  // const projectsCount = productionData?.teamState.activeProjects.length || 0;

  // Calculate action items count from meetings
  const actionItemsCount =
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    productionData?.meetings.reduce(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (sum: any, meeting: any) => sum + (meeting.actionItemsCount || 0),
      0
    ) || 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Team Meetings"
        value={meetingsCount}
        trend={{ value: 10, label: 'vs last week' }}
        icon={Users}
      />

      <StatCard
        title="Research Briefs"
        value={briefsCount}
        trend={{ value: 5, label: 'vs last week' }}
        icon={FileText}
      />

      <StatCard
        title="Action Items"
        value={actionItemsCount}
        description="Pending"
        icon={CheckCircle2}
      />

      <StatCard
        title="Investigation"
        value={investigationProgress}
        description="Completion"
        icon={Target}
      />
    </div>
  );
}
