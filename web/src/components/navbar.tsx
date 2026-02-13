"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useGamification } from "@/context/gamification-context"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Trophy, User, LogIn } from "lucide-react"

const navItems = [
  { name: "Dashboard", href: "/" },
  { name: "Team", href: "/team" },
  { name: "Projects", href: "/projects" },
  { name: "Research", href: "/research" },
  { name: "Resources", href: "/resources" },
]

export function Navbar() {
  const pathname = usePathname()
  const { isRussell, toggleRussell, points, level } = useGamification()

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-bold text-xl tracking-tight">
            BPR&D
          </Link>
          <div className="hidden md:flex gap-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  pathname === item.href
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isRussell && (
            <div className="flex items-center gap-2 px-3 py-1 bg-secondary rounded-full text-sm font-medium">
              <Trophy className="h-4 w-4 text-yellow-500" />
              <span>{points} pts</span>
              <span className="text-muted-foreground text-xs">Lvl {level}</span>
            </div>
          )}

          <Button
            variant={isRussell ? "outline" : "ghost"}
            size="sm"
            onClick={toggleRussell}
            className="gap-2"
          >
            {isRussell ? (
              <>
                <User className="h-4 w-4" />
                <span>Russell</span>
              </>
            ) : (
              <>
                <LogIn className="h-4 w-4" />
                <span>Login</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </nav>
  )
}
