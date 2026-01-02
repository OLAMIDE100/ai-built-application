import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { updateGameState, randomFood, INITIAL_SNAKE, GRID_SIZE } from '../utils/gameLogic';

// Simulated player AI - simple pathfinding towards food
function getAIDirection(snake, food, mode, currentDir) {
  const head = snake[0];
  const dx = food.x - head.x;
  const dy = food.y - head.y;

  // Simple AI: move towards food, avoid walls and self
  const possibleDirections = [
    { x: 1, y: 0 }, // right
    { x: -1, y: 0 }, // left
    { x: 0, y: 1 }, // down
    { x: 0, y: -1 }, // up
  ];

  // Filter out reverse direction
  const validDirections = possibleDirections.filter(dir => {
    if (dir.x === -currentDir.x && dir.y === -currentDir.y) return false;
    return true;
  });

  // Score each direction
  const scored = validDirections.map(dir => {
    const newHead = {
      x: head.x + dir.x,
      y: head.y + dir.y,
    };

    // Handle mode
    let wrappedHead = newHead;
    if (mode === 'pass') {
      wrappedHead = {
        x: (newHead.x + GRID_SIZE) % GRID_SIZE,
        y: (newHead.y + GRID_SIZE) % GRID_SIZE,
      };
    } else {
      if (newHead.x < 0 || newHead.y < 0 || newHead.x >= GRID_SIZE || newHead.y >= GRID_SIZE) {
        return { dir, score: -1000 }; // Wall collision
      }
    }

    // Check self collision
    if (snake.some(s => s.x === wrappedHead.x && s.y === wrappedHead.y)) {
      return { dir, score: -1000 };
    }

    // Distance to food (negative because closer is better)
    const distance = Math.abs(wrappedHead.x - food.x) + Math.abs(wrappedHead.y - food.y);
    return { dir, score: -distance };
  });

  // Sort by score and pick best
  scored.sort((a, b) => b.score - a.score);
  return scored[0]?.dir || currentDir;
}

// Simulated player game state
function useSimulatedPlayer(initialMode, playerId) {
  const [snake, setSnake] = useState(INITIAL_SNAKE);
  const [direction, setDirection] = useState({ x: 1, y: 0 });
  const [food, setFood] = useState(() => randomFood(INITIAL_SNAKE));
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [mode] = useState(initialMode);

  useEffect(() => {
    if (gameOver) return;

    const interval = setInterval(() => {
      setSnake(prev => {
        // AI decides direction
        const aiDir = getAIDirection(prev, food, mode, direction);
        setDirection(aiDir);

        const result = updateGameState(prev, aiDir, food, mode);

        if (result.gameOver) {
          setGameOver(true);
          // Restart after a delay
          setTimeout(() => {
            setSnake(INITIAL_SNAKE);
            setDirection({ x: 1, y: 0 });
            setFood(randomFood(INITIAL_SNAKE));
            setScore(0);
            setGameOver(false);
          }, 2000);
          return prev;
        }

        if (result.score > 0) {
          setScore(s => s + result.score);
        }

        setFood(result.food);
        return result.snake;
      });
    }, 120 + (playerId * 20)); // Slight variation in speed per player

    return () => clearInterval(interval);
  }, [food, gameOver, mode, direction, playerId]);

  return { snake, food, score, mode, gameOver };
}

function SimulatedPlayerGame({ player, playerId }) {
  const gameState = useSimulatedPlayer(player.mode || 'wall', playerId);

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-bold text-lg">{player.username}</h3>
        <span className="text-sm text-gray-600">Score: {gameState.score}</span>
      </div>
      <div className="flex justify-center">
        <div
          className="relative bg-gray-900"
          style={{
            width: GRID_SIZE * 20, // Smaller for watch mode
            height: GRID_SIZE * 20,
            backgroundImage: `
              linear-gradient(to right, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: `20px 20px`,
          }}
        >
          {gameState.snake.map((s, i) => (
            <div
              key={i}
              className="absolute bg-green-500"
              style={{
                width: 20,
                height: 20,
                left: s.x * 20,
                top: s.y * 20,
              }}
            />
          ))}
          <div
            className="absolute bg-red-500"
            style={{
              width: 20,
              height: 20,
              left: gameState.food.x * 20,
              top: gameState.food.y * 20,
            }}
          />
        </div>
      </div>
      <div className="text-center mt-2 text-sm text-gray-600">
        Mode: {gameState.mode === 'wall' ? 'Wall' : 'Pass Through'}
      </div>
    </div>
  );
}

export default function WatchMode() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  useEffect(() => {
    loadActivePlayers();
  }, []);

  const loadActivePlayers = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await api.getActivePlayers();
      if (result.success) {
        setPlayers(result.players);
      } else {
        setError('Failed to load active players');
      }
    } catch (err) {
      setError('An error occurred while loading players');
    } finally {
      setLoading(false);
    }
  };

  const handleWatchPlayer = async (playerId) => {
    try {
      const result = await api.watchPlayer(playerId);
      if (result.success) {
        setSelectedPlayer(result.player);
      }
    } catch (err) {
      setError('Failed to watch player');
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto mt-10 bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-center mb-6">Watch Players</h2>
        <div className="text-center">Loading...</div>
      </div>
    );
  }

  if (selectedPlayer) {
    return (
      <div className="max-w-4xl mx-auto mt-10">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Watching: {selectedPlayer.username}</h2>
            <button
              onClick={() => setSelectedPlayer(null)}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Back to List
            </button>
          </div>
          <SimulatedPlayerGame player={selectedPlayer} playerId={selectedPlayer.id} />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto mt-10 bg-white rounded-lg shadow-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Watch Players</h2>
        <button
          onClick={loadActivePlayers}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="text-red-600 text-center mb-4">{error}</div>
      )}

      {players.length === 0 ? (
        <div className="text-center text-gray-500">No active players at the moment.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {players.map((player) => (
            <div key={player.id} className="border border-gray-300 rounded-lg p-4 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-bold">{player.username}</h3>
                <span className="text-sm text-gray-600">Score: {player.score}</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Mode: {player.mode === 'wall' ? 'Wall' : 'Pass Through'}
              </p>
              <button
                onClick={() => handleWatchPlayer(player.id)}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Watch
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Show simulated games in grid view */}
      {players.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xl font-bold mb-4">Live Games</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {players.map((player, index) => (
              <SimulatedPlayerGame key={player.id} player={player} playerId={player.id} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

