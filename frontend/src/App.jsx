import { useState, useEffect } from 'react';
import { api } from './services/api';
import Login from './components/Login';
import Signup from './components/Signup';
import SnakeGame from './components/SnakeGame';
import Leaderboard from './components/Leaderboard';
import TopLeaderboard from './components/TopLeaderboard';

function App() {
  const [user, setUser] = useState(null);
  const [showSignup, setShowSignup] = useState(false);
  const [currentView, setCurrentView] = useState('game'); // 'game', 'leaderboard'
  const [scoreUpdateTrigger, setScoreUpdateTrigger] = useState(0);

  useEffect(() => {
    // Check if user is already logged in
    api.getCurrentUser().then(result => {
      if (result) {
        setUser(result);
      }
    });
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setShowSignup(false);
  };

  const handleSignup = (userData) => {
    setUser(userData);
    setShowSignup(false);
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    setCurrentView('game');
  };

  const handleScoreSubmit = async (score, mode) => {
    if (user) {
      await api.submitScore(score, mode);
      // Trigger leaderboard update
      setScoreUpdateTrigger(prev => prev + 1);
    }
  };

  const handleReturnToMenu = () => {
    // Optionally navigate to leaderboard after game over
    // setCurrentView('leaderboard');
    // Or just reset - the game will reset to initial state
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100">
        {showSignup ? (
          <Signup
            onSignup={handleSignup}
            onSwitchToLogin={() => setShowSignup(false)}
          />
        ) : (
          <Login
            onLogin={handleLogin}
            onSwitchToSignup={() => setShowSignup(true)}
          />
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-blue-600">Snake Game</h1>
              <div className="flex space-x-4">
                <button
                  onClick={() => setCurrentView('game')}
                  className={`px-4 py-2 rounded-md ${
                    currentView === 'game'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Play
                </button>
                <button
                  onClick={() => setCurrentView('leaderboard')}
                  className={`px-4 py-2 rounded-md ${
                    currentView === 'leaderboard'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Leaderboard
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, <span className="font-semibold">{user.username}</span></span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {currentView === 'game' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <SnakeGame 
                  onScoreSubmit={handleScoreSubmit} 
                  onReturnToMenu={handleReturnToMenu}
                />
              </div>
              <div className="lg:col-span-1">
                <TopLeaderboard onScoreUpdate={scoreUpdateTrigger} />
              </div>
            </div>
          </div>
        )}
        {currentView === 'leaderboard' && <Leaderboard />}
      </main>
    </div>
  );
}

export default App;

