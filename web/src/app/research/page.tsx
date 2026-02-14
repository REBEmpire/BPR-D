import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, TrendingUp, AlertTriangle } from "lucide-react"
import Link from "next/link"
import { getAllBriefs } from "@/lib/research"

export const dynamic = 'force-dynamic';

export default function ResearchPage() {
  const briefs = getAllBriefs();

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
      <div className="flex flex-col gap-2 mb-12">
        <h1 className="text-4xl font-bold tracking-tight">Daily Research Briefs</h1>
        <p className="text-muted-foreground text-lg">
          Intelligence assets, anomalies, and shenanigans from the BPR&D network.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-12">
        {Object.entries(briefsByCategory).map(([category, categoryBriefs]) => (
          <div key={category} className="space-y-6">
            <h2 className="text-2xl font-semibold border-b pb-2 flex items-center gap-2 capitalize">
              <span className="bg-primary/10 p-2 rounded-md">
                <FileText className="h-5 w-5 text-primary" />
              </span>
              {category.replace(/-/g, ' ')}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categoryBriefs.map((brief) => (
                <Link href={`/research/${brief.category}/${brief.slug}`} key={brief.slug} className="group">
                  <Card className="h-full flex flex-col transition-all hover:shadow-md hover:border-primary/50">
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
