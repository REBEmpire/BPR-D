import Image from "next/image"
import { cn } from "@/lib/utils"

interface AvatarProps {
  src: string
  name: string
  role: string
  className?: string
  status?: "online" | "offline"
}

export function Avatar({ src, name, role, className, status = "offline" }: AvatarProps) {
  return (
    <div className={cn("flex flex-col items-center", className)}>
      <div className="relative w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden border-4 border-background shadow-lg">
        <Image
          src={src}
          alt={name}
          fill
          className="object-cover"
        />
        {status === "online" && (
          <span className="absolute bottom-2 right-2 w-4 h-4 bg-green-500 rounded-full border-2 border-background" />
        )}
      </div>
      <div className="mt-3 text-center">
        <h3 className="font-bold text-lg">{name}</h3>
        <p className="text-sm text-muted-foreground">{role}</p>
      </div>
    </div>
  )
}
