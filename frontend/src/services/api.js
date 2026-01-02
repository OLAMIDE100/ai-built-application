// Centralized backend API mock service
// All backend calls should go through this service

// Mock storage (simulating a backend)
let mockUsers = [
  { id: 1, username: 'player1', email: 'player1@example.com', password: 'password123' },
  { id: 2, username: 'player2', email: 'player2@example.com', password: 'password123' },
];

let mockScores = [
  { id: 1, userId: 1, username: 'player1', score: 150, mode: 'wall', timestamp: Date.now() - 3600000 },
  { id: 2, userId: 2, username: 'player2', score: 120, mode: 'pass', timestamp: Date.now() - 7200000 },
  { id: 3, userId: 1, username: 'player1', score: 200, mode: 'wall', timestamp: Date.now() - 1800000 },
];

let currentUser = null;

// Simulate network delay
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  // Authentication
  async login(email, password) {
    await delay();
    const user = mockUsers.find(u => u.email === email && u.password === password);
    if (user) {
      currentUser = { ...user };
      delete currentUser.password;
      return { success: true, user: currentUser };
    }
    return { success: false, error: 'Invalid email or password' };
  },

  async signup(username, email, password) {
    await delay();
    if (mockUsers.find(u => u.email === email)) {
      return { success: false, error: 'Email already exists' };
    }
    if (mockUsers.find(u => u.username === username)) {
      return { success: false, error: 'Username already exists' };
    }
    const newUser = {
      id: mockUsers.length + 1,
      username,
      email,
      password,
    };
    mockUsers.push(newUser);
    currentUser = { ...newUser };
    delete currentUser.password;
    return { success: true, user: currentUser };
  },

  async logout() {
    await delay(100);
    currentUser = null;
    return { success: true };
  },

  async getCurrentUser() {
    await delay(100);
    return currentUser;
  },

  // Leaderboard
  async getLeaderboard(limit = 10) {
    await delay();
    const sorted = [...mockScores]
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map((score, index) => ({ ...score, rank: index + 1 }));
    return { success: true, leaderboard: sorted };
  },

  async submitScore(score, mode) {
    await delay();
    if (!currentUser) {
      return { success: false, error: 'Not authenticated' };
    }
    const newScore = {
      id: mockScores.length + 1,
      userId: currentUser.id,
      username: currentUser.username,
      score,
      mode,
      timestamp: Date.now(),
    };
    mockScores.push(newScore);
    return { success: true, score: newScore };
  },

  // Watching other players
  async getActivePlayers() {
    await delay();
    // Return mock active players
    return {
      success: true,
      players: [
        { id: 1, username: 'player1', score: 45, mode: 'wall' },
        { id: 2, username: 'player2', score: 32, mode: 'pass' },
        { id: 3, username: 'player3', score: 67, mode: 'wall' },
      ],
    };
  },

  async watchPlayer(playerId) {
    await delay();
    // Return mock player game state
    return {
      success: true,
      player: {
        id: playerId,
        username: `player${playerId}`,
        gameState: {
          snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }],
          food: { x: 10, y: 10 },
          score: 15,
          mode: 'wall',
        },
      },
    };
  },
};

