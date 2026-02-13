"use client"

import React, { createContext, useContext, useEffect, useState } from "react"

interface GameState {
  isRussell: boolean
  points: number
  completedQuests: string[]
  level: number
}

interface GamificationContextType extends GameState {
  toggleRussell: () => void
  completeQuest: (questId: string, reward: number) => void
  resetState: () => void
}

const defaultState: GameState = {
  isRussell: false,
  points: 0,
  completedQuests: [],
  level: 1,
}

const GamificationContext = createContext<GamificationContextType | undefined>(undefined)

export function GamificationProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<GameState>(defaultState)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    // Load from localStorage
    const saved = localStorage.getItem("bprd_state")
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        // eslint-disable-next-line
        setState(prev => ({ ...prev, ...parsed }))
      } catch (e) {
        console.error("Failed to parse gamification state", e)
      }
    }
    setLoaded(true)
  }, [])

  useEffect(() => {
    if (loaded) {
      localStorage.setItem("bprd_state", JSON.stringify({
        isRussell: state.isRussell,
        points: state.points,
        completedQuests: state.completedQuests,
      }))
    }
  }, [state, loaded])

  const toggleRussell = () => {
    setState(prev => ({ ...prev, isRussell: !prev.isRussell }))
  }

  const completeQuest = (questId: string, reward: number) => {
    setState(prev => {
      if (prev.completedQuests.includes(questId)) return prev
      const newPoints = prev.points + reward
      // Simple level calculation: 1 level every 100 points
      const newLevel = Math.floor(newPoints / 100) + 1
      return {
        ...prev,
        points: newPoints,
        completedQuests: [...prev.completedQuests, questId],
        level: newLevel,
      }
    })
  }

  const resetState = () => {
    setState(defaultState)
    localStorage.removeItem("bprd_state")
  }

  // Calculate level on the fly just in case
  const level = Math.floor(state.points / 100) + 1

  return (
    <GamificationContext.Provider value={{ ...state, level, toggleRussell, completeQuest, resetState }}>
      {children}
    </GamificationContext.Provider>
  )
}

export function useGamification() {
  const context = useContext(GamificationContext)
  if (context === undefined) {
    throw new Error("useGamification must be used within a GamificationProvider")
  }
  return context
}
