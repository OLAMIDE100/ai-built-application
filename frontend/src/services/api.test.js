import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from './api';

describe('API Service', () => {
  beforeEach(() => {
    // Reset API state by calling logout
    api.logout();
  });

  describe('Authentication', () => {
    it('should login with valid credentials', async () => {
      const result = await api.login('player1@example.com', 'password123');
      
      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user.username).toBe('player1');
      expect(result.user.password).toBeUndefined();
    });

    it('should fail login with invalid credentials', async () => {
      const result = await api.login('wrong@example.com', 'wrongpassword');
      
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should signup new user', async () => {
      const result = await api.signup('newuser', 'newuser@example.com', 'password123');
      
      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user.username).toBe('newuser');
    });

    it('should fail signup with existing email', async () => {
      const result = await api.signup('newuser2', 'player1@example.com', 'password123');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Email already exists');
    });

    it('should fail signup with existing username', async () => {
      const result = await api.signup('player1', 'newemail@example.com', 'password123');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Username already exists');
    });

    it('should logout user', async () => {
      await api.login('player1@example.com', 'password123');
      const result = await api.logout();
      
      expect(result.success).toBe(true);
      
      const currentUser = await api.getCurrentUser();
      expect(currentUser).toBeNull();
    });

    it('should get current user when logged in', async () => {
      await api.login('player1@example.com', 'password123');
      const user = await api.getCurrentUser();
      
      expect(user).toBeDefined();
      expect(user.username).toBe('player1');
    });
  });

  describe('Leaderboard', () => {
    it('should get leaderboard', async () => {
      const result = await api.getLeaderboard();
      
      expect(result.success).toBe(true);
      expect(result.leaderboard).toBeDefined();
      expect(Array.isArray(result.leaderboard)).toBe(true);
    });

    it('should return sorted leaderboard by score', async () => {
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
      const result = await api.getLeaderboard(5);
      
      expect(result.leaderboard.length).toBeLessThanOrEqual(5);
    });

    it('should submit score when logged in', async () => {
      await api.login('player1@example.com', 'password123');
      const result = await api.submitScore(100, 'wall');
      
      expect(result.success).toBe(true);
      expect(result.score).toBeDefined();
      expect(result.score.score).toBe(100);
      expect(result.score.mode).toBe('wall');
    });

    it('should fail to submit score when not logged in', async () => {
      const result = await api.submitScore(100, 'wall');
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Not authenticated');
    });
  });

  describe('Watch Mode', () => {
    it('should get active players', async () => {
      const result = await api.getActivePlayers();
      
      expect(result.success).toBe(true);
      expect(result.players).toBeDefined();
      expect(Array.isArray(result.players)).toBe(true);
    });

    it('should watch a player', async () => {
      const result = await api.watchPlayer(1);
      
      expect(result.success).toBe(true);
      expect(result.player).toBeDefined();
      expect(result.player.id).toBe(1);
      expect(result.player.gameState).toBeDefined();
    });
  });
});

