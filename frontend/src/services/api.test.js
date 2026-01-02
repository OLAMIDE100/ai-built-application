import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from './api';

// Mock fetch globally
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: vi.fn((key) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

// Replace global localStorage with mock
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('API Service', () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    localStorageMock.clear();
    global.fetch.mockClear();
    
    // Reset API state
    api.reset();
  });

  describe('Authentication', () => {
    it('should login with valid credentials', async () => {
      const mockUser = {
        id: 1,
        username: 'player1',
        email: 'player1@example.com',
      };
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          user: mockUser,
          token: 'mock-jwt-token',
        }),
      });

      const result = await api.login('player1@example.com', 'password123');
      
      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user.username).toBe('player1');
      expect(result.user.password).toBeUndefined();
      expect(localStorageMock.setItem).toHaveBeenCalledWith('authToken', 'mock-jwt-token');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('currentUser', JSON.stringify(mockUser));
    });

    it('should fail login with invalid credentials', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          detail: 'Invalid email or password',
        }),
      });

      const result = await api.login('wrong@example.com', 'wrongpassword');
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid email or password');
      expect(localStorageMock.setItem).not.toHaveBeenCalledWith('authToken', expect.any(String));
    });

    it('should signup new user', async () => {
      const mockUser = {
        id: 3,
        username: 'newuser',
        email: 'newuser@example.com',
      };
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          success: true,
          user: mockUser,
          token: 'mock-jwt-token',
        }),
      });

      const result = await api.signup('newuser', 'newuser@example.com', 'password123');
      
      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user.username).toBe('newuser');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('authToken', 'mock-jwt-token');
    });

    it('should fail signup with existing email', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({
          detail: 'Email already exists',
        }),
      });

      const result = await api.signup('newuser2', 'player1@example.com', 'password123');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Email already exists');
    });

    it('should fail signup with existing username', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({
          detail: 'Username already exists',
        }),
      });

      const result = await api.signup('player1', 'newemail@example.com', 'password123');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Username already exists');
    });

    it('should logout user', async () => {
      // Set up logged in state
      localStorageMock.setItem('authToken', 'mock-token');
      localStorageMock.setItem('currentUser', JSON.stringify({ id: 1, username: 'player1' }));
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
        }),
      });

      const result = await api.logout();
      
      expect(result.success).toBe(true);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('authToken');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('currentUser');
    });

    it('should get current user when logged in', async () => {
      const mockUser = {
        id: 1,
        username: 'player1',
        email: 'player1@example.com',
      };
      
      localStorageMock.setItem('authToken', 'mock-token');
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const user = await api.getCurrentUser();
      
      expect(user).toBeDefined();
      expect(user.username).toBe('player1');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('currentUser', JSON.stringify(mockUser));
    });

    it('should return cached user when token exists but API fails', async () => {
      const cachedUser = { id: 1, username: 'player1', email: 'player1@example.com' };
      localStorageMock.setItem('authToken', 'mock-token');
      localStorageMock.setItem('currentUser', JSON.stringify(cachedUser));
      
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          detail: 'Invalid token',
        }),
      });

      const user = await api.getCurrentUser();
      
      // Should clear token on failure
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('authToken');
      expect(user).toBeNull();
    });

    it('should return cached user when no token', async () => {
      const cachedUser = { id: 1, username: 'player1', email: 'player1@example.com' };
      localStorageMock.setItem('currentUser', JSON.stringify(cachedUser));
      
      const user = await api.getCurrentUser();
      
      expect(user).toEqual(cachedUser);
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  describe('Leaderboard', () => {
    it('should get leaderboard', async () => {
      const mockLeaderboard = [
        { id: 1, userId: 1, username: 'player1', score: 200, mode: 'wall', timestamp: Date.now(), rank: 1 },
        { id: 2, userId: 2, username: 'player2', score: 150, mode: 'pass', timestamp: Date.now(), rank: 2 },
      ];
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          leaderboard: mockLeaderboard,
        }),
      });

      const result = await api.getLeaderboard();
      
      expect(result.success).toBe(true);
      expect(result.leaderboard).toBeDefined();
      expect(Array.isArray(result.leaderboard)).toBe(true);
      expect(result.leaderboard.length).toBe(2);
    });

    it('should return sorted leaderboard by score', async () => {
      const mockLeaderboard = [
        { id: 1, userId: 1, username: 'player1', score: 200, mode: 'wall', timestamp: Date.now(), rank: 1 },
        { id: 2, userId: 2, username: 'player2', score: 150, mode: 'pass', timestamp: Date.now(), rank: 2 },
        { id: 3, userId: 3, username: 'player3', score: 100, mode: 'wall', timestamp: Date.now(), rank: 3 },
      ];
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          leaderboard: mockLeaderboard,
        }),
      });

      const result = await api.getLeaderboard();
      
      if (result.leaderboard.length > 1) {
        for (let i = 0; i < result.leaderboard.length - 1; i++) {
          expect(result.leaderboard[i].score).toBeGreaterThanOrEqual(
            result.leaderboard[i + 1].score
          );
        }
      }
    });

    it('should limit leaderboard results', async () => {
      const mockLeaderboard = [
        { id: 1, userId: 1, username: 'player1', score: 200, mode: 'wall', timestamp: Date.now(), rank: 1 },
        { id: 2, userId: 2, username: 'player2', score: 150, mode: 'pass', timestamp: Date.now(), rank: 2 },
      ];
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          leaderboard: mockLeaderboard,
        }),
      });

      const result = await api.getLeaderboard(5);
      
      expect(result.leaderboard.length).toBeLessThanOrEqual(5);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/leaderboard?limit=5'),
        expect.any(Object)
      );
    });

    it('should include mode filter when provided', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          leaderboard: [],
        }),
      });

      await api.getLeaderboard(10, 'wall');
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/leaderboard?limit=10&mode=wall'),
        expect.any(Object)
      );
    });

    it('should submit score when logged in', async () => {
      localStorageMock.setItem('authToken', 'mock-token');
      
      const mockScore = {
        id: 4,
        userId: 1,
        username: 'player1',
        score: 100,
        mode: 'wall',
        timestamp: Date.now(),
      };
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          success: true,
          score: mockScore,
        }),
      });

      const result = await api.submitScore(100, 'wall');
      
      expect(result.success).toBe(true);
      expect(result.score).toBeDefined();
      expect(result.score.score).toBe(100);
      expect(result.score.mode).toBe('wall');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/scores'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
          }),
        })
      );
    });

    it('should fail to submit score when not logged in', async () => {
      const result = await api.submitScore(100, 'wall');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Not authenticated');
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('should handle API error when submitting score', async () => {
      localStorageMock.setItem('authToken', 'mock-token');
      
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          detail: 'Invalid score',
        }),
      });

      const result = await api.submitScore(-10, 'wall');
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid score');
    });
  });

  describe('Active Players', () => {
    it('should get active players', async () => {
      const mockPlayers = [
        { id: 1, username: 'player1', score: 45, mode: 'wall' },
        { id: 2, username: 'player2', score: 32, mode: 'pass' },
      ];
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          players: mockPlayers,
        }),
      });

      const result = await api.getActivePlayers();
      
      expect(result.success).toBe(true);
      expect(result.players).toBeDefined();
      expect(Array.isArray(result.players)).toBe(true);
      expect(result.players.length).toBe(2);
    });

    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await api.getActivePlayers();
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });

    it('should handle fetch errors gracefully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('JSON parse error');
        },
      });

      const result = await api.getActivePlayers();
      
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle string error responses', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => 'Bad request',
      });

      const result = await api.login('test@example.com', 'password');
      
      expect(result.success).toBe(false);
      expect(result.error).toBe('Bad request');
    });

    it('should handle missing error details', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      const result = await api.getLeaderboard();
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Request failed with status 500');
    });
  });
});
