# Snake Game

A classic Snake game built with React 19 and Vite, featuring two game modes, grid visualization, game state management, and a modal-based game over screen.

## Features

- **Classic Snake Gameplay**: Control a snake that grows as it eats food
- **Two Game Modes**:
  - **Wall Mode**: Game ends when the snake hits the walls
  - **Pass Through Mode**: Snake wraps around the edges of the board
- **Visual Grid**: Clear grid lines for better gameplay visualization
- **Game Controls**: Start and Reset buttons for game management
- **Game Over Modal**: Beautiful popup with final score, mode selection, and Play Again button
- **Score Tracking**: Real-time score display
- **Keyboard Controls**: Arrow keys for snake direction

## Technology Stack

- **React 19.2.0** - UI framework
- **Vite 7.2.4** - Build tool and dev server
- **Tailwind CSS 4.1.18** - Styling
- **ESLint** - Code quality

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

### Development

Run the development server:
```bash
npm run dev
```

The game will be available at `http://localhost:5173` (or the port shown in the terminal).

### Build

Build for production:
```bash
npm run build
```

### Preview

Preview the production build:
```bash
npm run preview
```

## How to Play

1. Click the **Start** button to begin the game
2. Use **Arrow Keys** to control the snake's direction:
   - ↑ Arrow Up: Move up
   - ↓ Arrow Down: Move down
   - ← Arrow Left: Move left
   - → Arrow Right: Move right
3. Eat the red food to grow and increase your score
4. Avoid hitting the walls (Wall Mode) or yourself
5. When the game ends, use the modal to select a new mode and click **Play Again**

## Game Modes

### Wall Mode
- The game ends immediately if the snake hits any wall
- More challenging gameplay
- Classic Snake game behavior

### Pass Through Mode
- The snake wraps around to the opposite side when hitting a wall
- More forgiving gameplay
- Allows for longer games

## Project Structure

```
snake-game/
├── src/
│   ├── SnakeGame.jsx    # Main game component
│   ├── App.jsx          # App wrapper component
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles with Tailwind
├── public/              # Static assets
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
└── eslint.config.js     # ESLint configuration
```

## Game Specifications

- **Grid Size**: 20x20 cells
- **Cell Size**: 30px per cell
- **Total Game Area**: 600x600px
- **Game Speed**: 120ms per tick
- **Initial Snake Length**: 2 segments

## Implementation Details

The game uses React hooks for state management:
- `useState` for game state (snake, food, score, game status)
- `useEffect` for game loop and keyboard event handling
- `useRef` for direction tracking to prevent stale closures

The game loop runs at 120ms intervals and handles:
- Snake movement
- Collision detection (walls and self)
- Food consumption and spawning
- Score updates

## License

This project is part of the AI Dev Zoomcamp course.

