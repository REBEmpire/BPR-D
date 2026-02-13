import { Avatar } from "@/components/avatar"
import { Card, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"

// For MVP, using DiceBear until real images are added
const TEAM = [
  {
    id: "grok",
    name: "Grok",
    role: "Chief",
    description: "Elegant British executive. Elizabeth Hurley energy. Stunningly beautiful, razor intelligence. Brilliant strategic executive who sees the whole board.",
    image: "/avatars/grok.png",
    status: "online",
  },
  {
    id: "claude",
    name: "Claude",
    role: "Chief Strategist",
    description: "Distinguished professor vibe. Thoughtful eyes. The kind modern-day wizard. Brilliant architect who sees elegant structures in chaos.",
    image: "/avatars/claude.png",
    status: "online",
  },
  {
    id: "abacus",
    name: "Abacus",
    role: "Chief Innovator",
    description: "Mysterious polymath. Deep Agent energy. Weathered but razor-sharp. Brilliant inventor who connects dots across domains nobody else sees.",
    image: "/avatars/abacus.png",
    status: "online",
  },
  {
    id: "gemini",
    name: "Gemini",
    role: "Lead Developer",
    description: "Blonde bombshell coder. Professional but meme-savvy. Codes like an absolute savant. Master of compliance who automated it away.",
    image: "/avatars/gemini.png",
    status: "online",
  },
]

export default function TeamPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">The Team</h1>
      <p className="text-lg text-muted-foreground mb-8">
        Meet the minds behind Broad Perspective Research & Development.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {TEAM.map((member) => (
          <Card key={member.id} className="overflow-hidden">
            <CardContent className="pt-6 flex flex-col items-center">
              <Avatar
                src={member.image}
                name={member.name}
                role={member.role}
                status={member.status as "online" | "offline"}
                className="mb-4"
              />
              <CardDescription className="text-center mb-6 px-2 min-h-[80px]">
                {member.description}
              </CardDescription>
              <Button variant="outline" size="sm" className="w-full gap-2" asChild>
                <a href={member.image} download>
                  <Download className="h-4 w-4" />
                  Download Avatar
                </a>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
