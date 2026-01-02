// Game logic utilities - extracted for reusability and testing

export const GRID_SIZE = 20; // 20x20 grid
export const CELL_SIZE = 30; // px
export const INITIAL_SNAKE = [
  { x: 10, y: 10 },
  { x: 9, y: 10 },
];

export function randomFood(snake) {
  let pos;
  do {
    pos = {
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE),
    };
  } while (snake.some(s => s.x === pos.x && s.y === pos.y));
  return pos;
}

export function getNextHead(head, direction, mode) {
  let newHead = {
    x: head.x + direction.x,
    y: head.y + direction.y,
  };

  // Handle wall vs pass-through mode
  if (mode === "wall") {
    if (
      newHead.x < 0 ||
      newHead.y < 0 ||
      newHead.x >= GRID_SIZE ||
      newHead.y >= GRID_SIZE
    ) {
      return null; // Game over
    }
  } else {
    // pass-through mode (wrap around)
    newHead = {
      x: (newHead.x + GRID_SIZE) % GRID_SIZE,
      y: (newHead.y + GRID_SIZE) % GRID_SIZE,
    };
  }

  return newHead;
}

export function checkCollision(snake, newHead) {
  // Check self collision
  return snake.some(s => s.x === newHead.x && s.y === newHead.y);
}

export function updateGameState(snake, direction, food, mode) {
  const head = snake[0];
  const newHead = getNextHead(head, direction, mode);

  if (!newHead) {
    return { gameOver: true, snake, food, score: null };
  }

  if (checkCollision(snake, newHead)) {
    return { gameOver: true, snake, food, score: null };
  }

  let newSnake = [newHead, ...snake];
  let newFood = food;
  let scoreIncrease = 0;

  if (newHead.x === food.x && newHead.y === food.y) {
    scoreIncrease = 1;
    newFood = randomFood(newSnake);
  } else {
    newSnake.pop();
  }

  return {
    gameOver: false,
    snake: newSnake,
    food: newFood,
    score: scoreIncrease,
  };
}

export function isValidDirectionChange(currentDir, newDir) {
  // Prevent reversing into itself
  return !(currentDir.x === -newDir.x && currentDir.y === -newDir.y);
}

export function getDirectionFromKey(key, currentDirection) {
  const directions = {
    ArrowUp: { x: 0, y: -1 },
    ArrowDown: { x: 0, y: 1 },
    ArrowLeft: { x: -1, y: 0 },
    ArrowRight: { x: 1, y: 0 },
  };

  const newDir = directions[key];
  if (!newDir) return null;

  if (isValidDirectionChange(currentDirection, newDir)) {
    return newDir;
  }

  return null;
}

