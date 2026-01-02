import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await api.getLeaderboard();
      if (result.success) {
        setLeaderboard(result.leaderboard);
      } else {
        setError('Failed to load leaderboard');
      }
    } catch (err) {
      setError('An error occurred while loading leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const getModeLabel = (mode) => {
    return mode === 'wall' ? 'Wall Mode' : 'Pass Through Mode';
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto mt-10 bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold text-center mb-6">Leaderboard</h2>
        <div className="text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mt-10 bg-white rounded-lg shadow-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Leaderboard</h2>
        <button
          onClick={loadLeaderboard}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="text-red-600 text-center mb-4">{error}</div>
      )}

      {leaderboard.length === 0 ? (
        <div className="text-center text-gray-500">No scores yet. Be the first to play!</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 px-4 py-2 text-left">Rank</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Username</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Score</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Mode</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 font-semibold">
                    #{entry.rank}
                  </td>
                  <td className="border border-gray-300 px-4 py-2">{entry.username}</td>
                  <td className="border border-gray-300 px-4 py-2 font-bold text-blue-600">
                    {entry.score}
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    {getModeLabel(entry.mode)}
                  </td>
                  <td className="border border-gray-300 px-4 py-2 text-sm text-gray-600">
                    {formatDate(entry.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

