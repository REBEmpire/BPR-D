import * as React from "react"
import { cn } from "@/lib/utils"

export interface ScrollAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  viewportClassName?: string;
  orientation?: "vertical" | "horizontal" | "both";
}

const ScrollArea = React.forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className, viewportClassName, orientation = "vertical", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("relative overflow-hidden", className)}
        {...props}
      >
        <div
          className={cn(
            "h-full w-full rounded-[inherit]",
            orientation === "vertical" && "overflow-y-auto overflow-x-hidden",
            orientation === "horizontal" && "overflow-x-auto overflow-y-hidden",
            orientation === "both" && "overflow-auto",
            viewportClassName
          )}
        >
          {children}
        </div>
      </div>
    )
  }
)
ScrollArea.displayName = "ScrollArea"

export { ScrollArea }
