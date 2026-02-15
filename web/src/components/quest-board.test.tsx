import { ReactNode } from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { QuestBoard } from './quest-board'
import * as GamificationContext from '@/context/gamification-context'

// Mock the hook
vi.mock('@/context/gamification-context', () => ({
  useGamification: vi.fn(),
  GamificationProvider: ({ children }: { children: ReactNode }) => <div>{children}</div>
}))

describe('QuestBoard', () => {
  it('renders login prompt when not Russell', () => {
    vi.mocked(GamificationContext.useGamification).mockReturnValue({
      isRussell: false,
      points: 0,
      completedQuests: [],
      level: 1,
      toggleRussell: vi.fn(),
      completeQuest: vi.fn(),
      resetState: vi.fn(),
    })

    render(<QuestBoard />)
    expect(screen.getByText(/Login as Russell/i)).toBeInTheDocument()
  })

  it('renders quests when is Russell', () => {
    vi.mocked(GamificationContext.useGamification).mockReturnValue({
      isRussell: true,
      points: 0,
      completedQuests: [],
      level: 1,
      toggleRussell: vi.fn(),
      completeQuest: vi.fn(),
      resetState: vi.fn(),
    })

    render(<QuestBoard />)
    expect(screen.getByText('Ship First Research Brief')).toBeInTheDocument()
  })

  it('shows completed status correctly', () => {
    vi.mocked(GamificationContext.useGamification).mockReturnValue({
      isRussell: true,
      points: 50,
      completedQuests: ['q1'],
      level: 1,
      toggleRussell: vi.fn(),
      completeQuest: vi.fn(),
      resetState: vi.fn(),
    })

    render(<QuestBoard />)
    // 4 quests total, 1 completed. 3 "Complete" buttons.
    const completeButtons = screen.getAllByText('Complete')
    expect(completeButtons).toHaveLength(3)
    expect(screen.getByText('Done')).toBeInTheDocument()
  })

  it('calls completeQuest when button clicked', () => {
    const completeQuestMock = vi.fn()
    vi.mocked(GamificationContext.useGamification).mockReturnValue({
      isRussell: true,
      points: 0,
      completedQuests: [],
      level: 1,
      toggleRussell: vi.fn(),
      completeQuest: completeQuestMock,
      resetState: vi.fn(),
    })

    render(<QuestBoard />)
    const completeButtons = screen.getAllByText('Complete')
    fireEvent.click(completeButtons[0])

    expect(completeQuestMock).toHaveBeenCalledWith('q1', 50)
  })
})
