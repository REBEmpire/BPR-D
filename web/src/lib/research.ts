/* eslint-disable @typescript-eslint/no-explicit-any */
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';
import gfm from 'remark-gfm';

const contentDirectory = path.join(process.cwd(), 'src/content/research');

export interface DailyBrief {
  slug: string;
  category: string;
  date: string;
  title: string;
  summary: string;
  relevance: string;
  incomePotential: string;
  content: string;
  frontmatter: any;
}

export function getAllBriefs(): DailyBrief[] {
  if (!fs.existsSync(contentDirectory)) {
    console.warn(`Content directory not found: ${contentDirectory}`);
    return [];
  }

  const briefs: DailyBrief[] = [];

  try {
    const categories = fs.readdirSync(contentDirectory);

    categories.forEach(category => {
      const categoryPath = path.join(contentDirectory, category);
      if (!fs.statSync(categoryPath).isDirectory()) return;

      const files = fs.readdirSync(categoryPath);

      files.forEach(file => {
        if (!file.endsWith('.md')) return;

        const fullPath = path.join(categoryPath, file);
        const fileContents = fs.readFileSync(fullPath, 'utf8');
        const { data, content } = matter(fileContents);

        // Extract title from first H1 if not in frontmatter
        let title = data.title || file.replace('.md', '');
        const titleMatch = content.match(/^#\s+(.+)$/m);
        if (titleMatch) title = titleMatch[1];
        else if (!data.title) title = file.replace('.md', '');

        // Extract one-sentence summary if not in frontmatter
        let summary = data.summary || '';
        const summaryMatch = content.match(/\*\*One-Sentence Summary\*\*\s*\n(.+)/);
        if (summaryMatch) summary = summaryMatch[1];

        // Extract Relevance
        let relevance = data.relevance || 'Unknown';
        const relMatch = content.match(/\*\*Relevance to BPR&D:\*\*\s*(.+)/);
        if (relMatch) relevance = relMatch[1].trim();

        // Extract Income Potential
        let incomePotential = data.incomePotential || 'Unknown';
        const incMatch = content.match(/\*\*Income Potential:\*\*\s*(.+)/);
        if (incMatch) incomePotential = incMatch[1].trim();

        // Extract Date from filename [YYYY-MM-DD]-[slug]
        const dateMatch = file.match(/^(\d{4}-\d{2}-\d{2})/);
        const date = dateMatch ? dateMatch[1] : 'Unknown';

        briefs.push({
          slug: file.replace('.md', ''),
          category,
          date,
          title: title.replace(/^\d{4}-\d{2}-\d{2}\s*-\s*/, ''), // Remove date prefix from title if present
          summary,
          relevance,
          incomePotential,
          content,
          frontmatter: data,
        });
      });
    });
  } catch (error) {
    console.error('Error reading briefs:', error);
    return [];
  }

  return briefs.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export async function getBriefContent(category: string, slug: string): Promise<DailyBrief | null> {
  // Try to find the file directly first
  const fullPath = path.join(contentDirectory, category, `${slug}.md`);

  if (!fs.existsSync(fullPath)) {
    // If exact slug fails, try to find a file that *ends* with the slug (handling date prefix)
    // Actually, the slug passed in *should* be the full filename without extension based on getAllBriefs
    return null;
  }

  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, content } = matter(fileContents);

  const processedContent = await remark()
    .use(html)
    .use(gfm)
    .process(content);

  const contentHtml = processedContent.toString();

  // Extract metadata
  let title = data.title || slug;
  const titleMatch = content.match(/^#\s+(.+)$/m);
  if (titleMatch) title = titleMatch[1];

  let summary = data.summary || '';
  const summaryMatch = content.match(/\*\*One-Sentence Summary\*\*\s*\n(.+)/);
  if (summaryMatch) summary = summaryMatch[1];

  let relevance = data.relevance || 'Unknown';
  const relMatch = content.match(/\*\*Relevance to BPR&D:\*\*\s*(.+)/);
  if (relMatch) relevance = relMatch[1].trim();

  let incomePotential = data.incomePotential || 'Unknown';
  const incMatch = content.match(/\*\*Income Potential:\*\*\s*(.+)/);
  if (incMatch) incomePotential = incMatch[1].trim();

  const dateMatch = slug.match(/^(\d{4}-\d{2}-\d{2})/);
  const date = dateMatch ? dateMatch[1] : 'Unknown';

  return {
    slug,
    category,
    date,
    title: title.replace(/^\d{4}-\d{2}-\d{2}\s*-\s*/, ''),
    summary,
    relevance,
    incomePotential,
    content: contentHtml,
    frontmatter: data,
  };
}
