import { useEffect, useRef, useState } from "react";
import {
  GRID_SIZE,
  CELL_SIZE,
  INITIAL_SNAKE,
  randomFood,
  updateGameState,
  getDirectionFromKey,
} from "../utils/gameLogic";

export default function SnakeGame({
  mode: initialMode = "wall",
  onScoreSubmit,
  controlled = false,
  externalDirection = null,
  onGameOver = null,
  onReturnToMenu = null,
  showControls = true,
  title = "Snake Game",
}) {
  const [snake, setSnake] = useState(INITIAL_SNAKE);
  const [direction, setDirection] = useState({ x: 1, y: 0 });
  const [food, setFood] = useState(() => randomFood(INITIAL_SNAKE));
  const [gameOver, setGameOver] = useState(false);
  const [score, setScore] = useState(0);
  const [mode, setMode] = useState(initialMode);
  const [gameStarted, setGameStarted] = useState(false);
  const [paused, setPaused] = useState(false);

  const directionRef = useRef(direction);
  directionRef.current = direction;

  // Use external direction if in controlled mode
  const currentDirection = controlled && externalDirection ? externalDirection : directionRef.current;

  useEffect(() => {
    if (controlled) return; // Don't listen to keyboard in controlled mode

    const handleKey = (e) => {
      const newDir = getDirectionFromKey(e.key, directionRef.current);
      if (newDir) {
        setDirection(newDir);
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [controlled]);

  useEffect(() => {
    if (gameOver || !gameStarted || paused) return;

    const interval = setInterval(() => {
      setSnake(prev => {
        const result = updateGameState(prev, currentDirection, food, mode);
        
        if (result.gameOver) {
          setGameOver(true);
          if (onGameOver) {
            onGameOver(score);
          }
          if (onScoreSubmit && score > 0) {
            onScoreSubmit(score, mode);
          }
          return prev;
        }

        if (result.score > 0) {
          setScore(s => s + result.score);
        }

        setFood(result.food);
        return result.snake;
      });
    }, 120);

    return () => clearInterval(interval);
  }, [food, gameOver, mode, gameStarted, paused, currentDirection, onGameOver, onScoreSubmit, score]);

  const resetGame = () => {
    setSnake(INITIAL_SNAKE);
    setDirection({ x: 1, y: 0 });
    setFood(randomFood(INITIAL_SNAKE));
    setGameOver(false);
    setScore(0);
    setGameStarted(false);
    setPaused(false);
  };

  const playAgain = () => {
    setSnake(INITIAL_SNAKE);
    setDirection({ x: 1, y: 0 });
    setFood(randomFood(INITIAL_SNAKE));
    setGameOver(false);
    setScore(0);
    setGameStarted(true);
    setPaused(false);
  };

  const toggleGame = () => {
    if (!gameStarted) {
      // Start the game
      setGameStarted(true);
      setGameOver(false);
      setPaused(false);
    } else if (paused) {
      // Resume the game
      setPaused(false);
    } else {
      // Pause the game
      setPaused(true);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 mt-10 relative">
      <h1 className="text-3xl font-bold">{title}</h1>

      <div className="flex gap-2 items-center">
        <span className="text-sm font-medium">Game Mode:</span>
        <span className="text-sm font-semibold text-blue-600">
          {mode === "wall" ? "Wall Mode" : "Pass Through Mode"}
        </span>
      </div>

      <div
        className="relative bg-gray-900"
        style={{
          width: GRID_SIZE * CELL_SIZE,
          height: GRID_SIZE * CELL_SIZE,
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: `${CELL_SIZE}px ${CELL_SIZE}px`,
        }}
      >
        {snake.map((s, i) => (
          <div
            key={i}
            className="absolute bg-green-500"
            style={{
              width: CELL_SIZE,
              height: CELL_SIZE,
              left: s.x * CELL_SIZE,
              top: s.y * CELL_SIZE,
            }}
          />
        ))}
        <div
          className="absolute bg-red-500"
          style={{
            width: CELL_SIZE,
            height: CELL_SIZE,
            left: food.x * CELL_SIZE,
            top: food.y * CELL_SIZE,
          }}
        />
      </div>

      <div className="text-lg">Score: {score}</div>
      {paused && gameStarted && (
        <div className="text-lg font-semibold text-yellow-600">PAUSED</div>
      )}

      {showControls && (
        <div className="flex gap-3 items-center">
          <button
            onClick={toggleGame}
            className={`px-4 py-2 text-white rounded hover:opacity-90 ${
              !gameStarted
                ? 'bg-green-600 hover:bg-green-700'
                : paused
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-yellow-600 hover:bg-yellow-700'
            }`}
          >
            {!gameStarted ? 'Start' : paused ? 'Resume' : 'Pause'}
          </button>
          {gameStarted && (
            <button
              onClick={resetGame}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Reset
            </button>
          )}
        </div>
      )}

      {gameOver && showControls && (
        <>
          {/* Backdrop overlay */}
          <div className="fixed inset-0 bg-black bg-opacity-50 z-40" />
          
          {/* Modal popup */}
          <div className="fixed inset-0 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4 flex flex-col items-center gap-4">
              <h2 className="text-3xl font-bold text-red-600">Game Over!</h2>
              <p className="text-xl text-gray-700">Final Score: <span className="font-semibold">{score}</span></p>
              
              <div className="flex flex-col gap-2 w-full items-center">
                <label htmlFor="mode-select-popup" className="text-sm font-medium text-gray-700">
                  Select Game Mode:
                </label>
                <select
                  id="mode-select-popup"
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                  className="px-4 py-2 rounded bg-white border-2 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full text-center"
                >
                  <option value="wall">Wall Mode</option>
                  <option value="pass">Pass Through Mode</option>
                </select>
              </div>

              <div className="flex flex-col gap-3 w-full">
                <button
                  onClick={playAgain}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold text-lg transition-colors w-full"
                >
                  Play Again
                </button>
                <button
                  onClick={() => {
                    resetGame();
                    if (onReturnToMenu) {
                      onReturnToMenu();
                    }
                  }}
                  className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-semibold text-lg transition-colors w-full"
                >
                  Return to Menu
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

