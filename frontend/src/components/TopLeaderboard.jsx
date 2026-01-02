import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function TopLeaderboard({ onScoreUpdate }) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadLeaderboard = async () => {
    try {
      const result = await api.getLeaderboard(5); // Get top 5
      if (result.success) {
        setLeaderboard(result.leaderboard);
      }
    } catch (err) {
      console.error('Failed to load leaderboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeaderboard();
    
    // Refresh every 5 seconds for real-time updates
    const interval = setInterval(loadLeaderboard, 5000);
    
    return () => clearInterval(interval);
  }, []);

  // Update when a new score is submitted
  useEffect(() => {
    if (onScoreUpdate !== undefined && onScoreUpdate > 0) {
      loadLeaderboard();
    }
  }, [onScoreUpdate]);

  if (loading && leaderboard.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-bold mb-3">Top 5 Leaderboard</h3>
        <div className="text-center text-gray-500 text-sm">Loading...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-bold mb-3">Top 5 Leaderboard</h3>
      {leaderboard.length === 0 ? (
        <div className="text-center text-gray-500 text-sm">No scores yet</div>
      ) : (
        <div className="space-y-2">
          {leaderboard.map((entry) => (
            <div
              key={entry.id}
              className="flex justify-between items-center p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="font-bold text-gray-600 w-6">#{entry.rank}</span>
                <span className="text-sm font-medium">{entry.username}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  {entry.mode === 'wall' ? 'Wall' : 'Pass'}
                </span>
                <span className="font-bold text-blue-600">{entry.score}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

