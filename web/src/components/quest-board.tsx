"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useGamification } from "@/context/gamification-context"
import { CheckCircle2, Circle } from "lucide-react"

const QUESTS = [
  { id: "q1", title: "Ship First Research Brief", points: 50 },
  { id: "q2", title: "Review Team Profiles", points: 20 },
  { id: "q3", title: "Test n8n Integration", points: 30 },
  { id: "q4", title: "Visit All Project Pages", points: 40 },
]

export function QuestBoard() {
  const { isRussell, completedQuests, completeQuest } = useGamification()

  if (!isRussell) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Active Quests</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Login as Russell to view and complete quests.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Active Quests</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {QUESTS.map((quest) => {
          const isCompleted = completedQuests.includes(quest.id)
          return (
            <div
              key={quest.id}
              className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                {isCompleted ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <Circle className="h-5 w-5 text-muted-foreground" />
                )}
                <div className="flex flex-col">
                  <span className={isCompleted ? "line-through text-muted-foreground" : "font-medium"}>
                    {quest.title}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    +{quest.points} XP
                  </span>
                </div>
              </div>

              {!isCompleted && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => completeQuest(quest.id, quest.points)}
                >
                  Complete
                </Button>
              )}
              {isCompleted && (
                <Badge variant="secondary">Done</Badge>
              )}
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
