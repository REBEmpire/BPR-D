import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, TrendingUp, AlertTriangle, BarChart3 } from "lucide-react"
import Link from "next/link"
import { getAllBriefs } from "@/lib/research"
import fs from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic';

export default function ResearchPage() {
  const briefs = getAllBriefs();

  // Read production metrics
  let totalBriefs = briefs.length;
  let mostActiveCategory = '';
  let recentPublicationRate = '0 this week';

  try {
    const dataPath = path.join(process.cwd(), 'src/content/production.json');
    if (fs.existsSync(dataPath)) {
      const fileContent = fs.readFileSync(dataPath, 'utf-8');
      const data = JSON.parse(fileContent);
      if (data.researchMetrics) {
        totalBriefs = data.researchMetrics.totalBriefs || briefs.length;

        // Find most active category
        const categoryCounts = data.researchMetrics.categoryCounts || {};
        const maxCount = Math.max(...Object.values(categoryCounts).map(Number));
        mostActiveCategory = Object.entries(categoryCounts).find(
          ([_, count]) => count === maxCount
        )?.[0] || '';

        // Count recent briefs (last 7 days)
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        const recentCount = data.researchMetrics.recentBriefs?.filter((brief: any) => {
          const briefDate = new Date(brief.date);
          return briefDate >= weekAgo;
        }).length || 0;
        recentPublicationRate = recentCount > 0 ? `${recentCount} this week` : '0 this week';
      }
    }
  } catch (err) {
    console.warn('Error reading research metrics:', err);
  }

  // Group briefs by category
  const briefsByCategory = briefs.reduce((acc, brief) => {
    if (!acc[brief.category]) {
      acc[brief.category] = [];
    }
    acc[brief.category].push(brief);
    return acc;
  }, {} as Record<string, typeof briefs>);

  return (
    <div className="container mx-auto p-8 max-w-7xl">
      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-4xl font-bold tracking-tight">Daily Research Briefs</h1>
        <p className="text-muted-foreground text-lg">
          Intelligence assets, anomalies, and shenanigans from the BPR&D network.
        </p>
      </div>

      {/* Stats Banner */}
      {briefs.length > 0 && (
        <div className="glass-card rounded-2xl p-6 mb-12">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-bold">Research Overview</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <p className="text-3xl font-black neon-pulse text-primary">{totalBriefs}</p>
              <p className="text-sm text-muted-foreground mt-1">Total Briefs Published</p>
            </div>
            {mostActiveCategory && (
              <div>
                <p className="text-2xl font-bold capitalize">{mostActiveCategory.replace(/-/g, ' ')}</p>
                <p className="text-sm text-muted-foreground mt-1">Most Active Category</p>
              </div>
            )}
            <div>
              <p className="text-2xl font-bold">{recentPublicationRate}</p>
              <p className="text-sm text-muted-foreground mt-1">Recent Publication Rate</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-12">
        {Object.entries(briefsByCategory).map(([category, categoryBriefs]) => (
          <div key={category} className="space-y-6">
            <h2 className="text-2xl font-semibold border-b pb-2 flex items-center gap-2 capitalize data-stream">
              <span className="bg-primary/10 p-2 rounded-md">
                <FileText className="h-5 w-5 text-primary" />
              </span>
              {category.replace(/-/g, ' ')}
              <Badge variant="outline" className="ml-auto">{categoryBriefs.length} briefs</Badge>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categoryBriefs.map((brief) => (
                <Link href={`/research/${brief.category}/${brief.slug}`} key={brief.slug} className="group">
                  <Card className="h-full flex flex-col transition-all hover:shadow-md hover:border-primary/50 hover:shadow-primary/10">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start gap-4">
                        <Badge variant="secondary" className="font-mono text-xs">
                          {brief.date}
                        </Badge>
                        <Badge
                          variant={
                            brief.relevance?.includes('High') ? 'default' :
                            brief.relevance?.includes('Medium') ? 'secondary' : 'outline'
                          }
                          className="text-[10px] px-1.5 h-5"
                        >
                          {brief.relevance?.replace('Relevance to BPR&D:', '').trim() || 'Research'}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg leading-snug group-hover:text-primary transition-colors mt-2">
                        {brief.title.replace(/^#\s*/, '')}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-grow pb-3">
                      <p className="text-sm text-muted-foreground line-clamp-3">
                        {brief.summary.replace(/^\*\*One-Sentence Summary\*\*\s*/, '')}
                      </p>
                    </CardContent>
                    <CardFooter className="pt-0 text-xs text-muted-foreground flex justify-between items-center border-t p-4 mt-auto bg-muted/5">
                      <div className="flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        <span className="truncate max-w-[120px]" title={brief.incomePotential}>
                          {brief.incomePotential?.replace('Income Potential:', '').trim() || 'Unknown'}
                        </span>
                      </div>
                      <span className="group-hover:translate-x-1 transition-transform">
                        Read Brief →
                      </span>
                    </CardFooter>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      {briefs.length === 0 && (
        <div className="text-center py-20 text-muted-foreground">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No Research Found</h3>
          <p>Run <code>npm run sync-research</code> to populate the database.</p>
        </div>
      )}
    </div>
  )
}
