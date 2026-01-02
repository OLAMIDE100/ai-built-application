import { describe, it, expect } from 'vitest';
import {
  GRID_SIZE,
  INITIAL_SNAKE,
  randomFood,
  getNextHead,
  checkCollision,
  updateGameState,
  isValidDirectionChange,
  getDirectionFromKey,
} from './gameLogic';

describe('gameLogic', () => {
  describe('randomFood', () => {
    it('should generate food not on snake', () => {
      const snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }];
      const food = randomFood(snake);
      
      expect(food).toBeDefined();
      expect(food.x).toBeGreaterThanOrEqual(0);
      expect(food.x).toBeLessThan(GRID_SIZE);
      expect(food.y).toBeGreaterThanOrEqual(0);
      expect(food.y).toBeLessThan(GRID_SIZE);
      expect(snake.some(s => s.x === food.x && s.y === food.y)).toBe(false);
    });
  });

  describe('getNextHead', () => {
    it('should move head in wall mode', () => {
      const head = { x: 10, y: 10 };
      const direction = { x: 1, y: 0 };
      const newHead = getNextHead(head, direction, 'wall');
      
      expect(newHead).toEqual({ x: 11, y: 10 });
    });

    it('should return null when hitting wall in wall mode', () => {
      const head = { x: GRID_SIZE - 1, y: 10 };
      const direction = { x: 1, y: 0 };
      const newHead = getNextHead(head, direction, 'wall');
      
      expect(newHead).toBeNull();
    });

    it('should wrap around in pass-through mode', () => {
      const head = { x: GRID_SIZE - 1, y: 10 };
      const direction = { x: 1, y: 0 };
      const newHead = getNextHead(head, direction, 'pass');
      
      expect(newHead).toEqual({ x: 0, y: 10 });
    });

    it('should wrap around from negative in pass-through mode', () => {
      const head = { x: 0, y: 10 };
      const direction = { x: -1, y: 0 };
      const newHead = getNextHead(head, direction, 'pass');
      
      expect(newHead).toEqual({ x: GRID_SIZE - 1, y: 10 });
    });
  });

  describe('checkCollision', () => {
    it('should detect self collision', () => {
      const snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }];
      const newHead = { x: 9, y: 10 };
      
      expect(checkCollision(snake, newHead)).toBe(true);
    });

    it('should not detect collision when head is not on snake', () => {
      const snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }];
      const newHead = { x: 11, y: 10 };
      
      expect(checkCollision(snake, newHead)).toBe(false);
    });
  });

  describe('updateGameState', () => {
    it('should move snake forward', () => {
      const snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }];
      const direction = { x: 1, y: 0 };
      const food = { x: 15, y: 15 };
      
      const result = updateGameState(snake, direction, food, 'wall');
      
      expect(result.gameOver).toBe(false);
      expect(result.snake.length).toBe(2);
      expect(result.snake[0]).toEqual({ x: 11, y: 10 });
    });

    it('should grow snake when eating food', () => {
      const snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }];
      const direction = { x: 1, y: 0 };
      const food = { x: 11, y: 10 };
      
      const result = updateGameState(snake, direction, food, 'wall');
      
      expect(result.gameOver).toBe(false);
      expect(result.snake.length).toBe(3);
      expect(result.score).toBe(1);
      expect(result.food).not.toEqual(food);
    });

    it('should detect game over on wall collision', () => {
      const snake = [{ x: GRID_SIZE - 1, y: 10 }, { x: GRID_SIZE - 2, y: 10 }];
      const direction = { x: 1, y: 0 };
      const food = { x: 5, y: 5 };
      
      const result = updateGameState(snake, direction, food, 'wall');
      
      expect(result.gameOver).toBe(true);
    });

    it('should detect game over on self collision', () => {
      const snake = [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }];
      const direction = { x: -1, y: 0 };
      const food = { x: 5, y: 5 };
      
      const result = updateGameState(snake, direction, food, 'wall');
      
      expect(result.gameOver).toBe(true);
    });
  });

  describe('isValidDirectionChange', () => {
    it('should allow perpendicular direction changes', () => {
      const current = { x: 1, y: 0 };
      const newDir = { x: 0, y: 1 };
      
      expect(isValidDirectionChange(current, newDir)).toBe(true);
    });

    it('should prevent reverse direction', () => {
      const current = { x: 1, y: 0 };
      const newDir = { x: -1, y: 0 };
      
      expect(isValidDirectionChange(current, newDir)).toBe(false);
    });

    it('should allow same direction', () => {
      const current = { x: 1, y: 0 };
      const newDir = { x: 1, y: 0 };
      
      expect(isValidDirectionChange(current, newDir)).toBe(true);
    });
  });

  describe('getDirectionFromKey', () => {
    it('should return correct direction for arrow keys', () => {
      const current = { x: 1, y: 0 };
      
      expect(getDirectionFromKey('ArrowUp', current)).toEqual({ x: 0, y: -1 });
      expect(getDirectionFromKey('ArrowDown', current)).toEqual({ x: 0, y: 1 });
      expect(getDirectionFromKey('ArrowLeft', current)).toBeNull(); // Reverse direction
      expect(getDirectionFromKey('ArrowRight', current)).toEqual({ x: 1, y: 0 });
    });

    it('should return null for invalid keys', () => {
      const current = { x: 1, y: 0 };
      
      expect(getDirectionFromKey('a', current)).toBeNull();
      expect(getDirectionFromKey('Enter', current)).toBeNull();
    });

    it('should prevent reverse direction', () => {
      const current = { x: 1, y: 0 };
      
      expect(getDirectionFromKey('ArrowLeft', current)).toBeNull();
    });
  });
});

