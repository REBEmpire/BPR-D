import { getBriefContent, getAllBriefs } from "@/lib/research"
import { notFound } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { Calendar, FileText, ArrowLeft, ArrowUpRight } from "lucide-react"
import Link from "next/link"

export const dynamic = 'force-dynamic';

interface PageProps {
  params: Promise<{
    category: string;
    slug: string;
  }>
}

export default async function BriefPage({ params }: PageProps) {
  const { category, slug } = await params
  const brief = await getBriefContent(category, slug)

  if (!brief) {
    notFound()
  }

  return (
    <article className="container mx-auto max-w-4xl px-6 py-12 md:py-20 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Back Link */}
      <Link
        href="/research"
        className="group inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground mb-8 transition-colors no-underline"
      >
        <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
        Back to Research Index
      </Link>

      {/* Hero Section */}
      <header className="mb-12 space-y-6">
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono uppercase tracking-wider text-muted-foreground">
          <span className="flex items-center gap-1.5 bg-secondary/30 px-2 py-1 rounded">
            <Calendar className="h-3 w-3" />
            {brief.date}
          </span>
          <span className="flex items-center gap-1.5 bg-secondary/30 px-2 py-1 rounded">
            <FileText className="h-3 w-3" />
            {brief.category.replace(/-/g, ' ')}
          </span>
          {brief.relevance && (
            <span className={`px-2 py-1 rounded border ${
              brief.relevance.includes('High') ? 'border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400' :
              brief.relevance.includes('Medium') ? 'border-yellow-500/20 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400' :
              'border-zinc-500/20 bg-zinc-500/10'
            }`}>
              {brief.relevance.replace('Relevance to BPR&D:', '')}
            </span>
          )}
        </div>

        <h1 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-foreground">
          {brief.title.replace(/^\d{4}-\d{2}-\d{2}\s*-\s*/, '')}
        </h1>

        <div className="relative pl-6 border-l-4 border-primary/20 py-1">
          <p className="text-xl md:text-2xl font-light leading-relaxed text-muted-foreground italic">
            {brief.summary.replace('**One-Sentence Summary**', '').trim()}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div
        className="prose prose-zinc dark:prose-invert max-w-none
        prose-headings:font-bold prose-headings:tracking-tight prose-headings:scroll-m-20
        prose-h2:text-3xl prose-h2:mt-16 prose-h2:mb-6 prose-h2:pb-2 prose-h2:border-b
        prose-h3:text-xl prose-h3:mt-10 prose-h3:mb-4 prose-h3:text-foreground
        prose-p:leading-7 prose-p:my-6 prose-p:text-base
        prose-ul:my-6 prose-ul:list-disc prose-ul:pl-6
        prose-li:my-2 prose-li:text-base
        prose-strong:font-bold prose-strong:text-foreground
        prose-a:font-medium prose-a:text-primary prose-a:no-underline hover:prose-a:underline
        prose-blockquote:border-l-4 prose-blockquote:border-primary/20 prose-blockquote:pl-6 prose-blockquote:italic prose-blockquote:text-muted-foreground
        [&>ul>li]:marker:text-primary/50"
        dangerouslySetInnerHTML={{ __html: brief.content }}
      />

      {/* Metadata Footer */}
      <footer className="mt-20 pt-8 border-t border-border grid gap-6 md:grid-cols-2 text-sm text-muted-foreground">
        <div className="space-y-2">
          <h4 className="font-semibold text-foreground uppercase tracking-wider text-xs">Income Potential</h4>
          <p className="flex items-center gap-2">
            <ArrowUpRight className="h-4 w-4" />
            {brief.incomePotential?.replace('Income Potential:', '').trim() || 'Not assessed'}
          </p>
        </div>
        <div className="space-y-2 md:text-right">
          <h4 className="font-semibold text-foreground uppercase tracking-wider text-xs">Brief ID</h4>
          <code className="bg-muted px-2 py-1 rounded font-mono text-xs">{brief.slug}</code>
        </div>
      </footer>
    </article>
  )
}

export async function generateStaticParams() {
  const briefs = getAllBriefs()
  return briefs.map((brief) => ({
    category: brief.category,
    slug: brief.slug,
  }))
}
