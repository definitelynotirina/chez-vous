import { useState } from 'react';
import { analyzeAddress } from '../services/api';

function Home() {
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!address.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeAddress(address);
      setResult(data);
    } catch (err) {
      setError(err.error || 'Failed to analyze address');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Logo text will go here */}
        <h1 className="text-6xl font-light mb-12 tracking-wide">Chez-Vous</h1>

        <form onSubmit={handleSubmit} className="w-full">
          <div className="relative">
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Enter a Paris address..."
              className="w-full px-6 py-4 text-lg border-2 border-black focus:outline-none focus:border-[#b8020a] transition-colors"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !address.trim()}
            className="mt-6 px-8 py-3 bg-black text-white hover:bg-[#b8020a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Analyzing...' : 'Analyze Neighborhood'}
          </button>
        </form>

        <p className="mt-8 text-sm text-gray-600">
          Try: "10 Rue de Rivoli, 75001 Paris" or "Montmartre"
        </p>

        {error && (
          <div className="mt-8 p-4 bg-red-100 border-2 border-red-600 text-red-700">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-12 text-left p-8 bg-white border-2 border-black">
            <h2 className="text-2xl font-semibold mb-4">Analysis Results</h2>

            <div className="mb-6">
              <h3 className="font-semibold mb-2">Location</h3>
              <p className="text-sm">Arrondissement: {result.geo_data?.arrondissement || 'Unknown'}</p>
              <p className="text-sm text-gray-600">{result.geo_data?.full_address}</p>
            </div>

            {result.analysis && (
              <div>
                <h3 className="font-semibold mb-2">Overview</h3>
                <p className="text-sm mb-4">{result.analysis.overview?.description}</p>
                <p className="text-xs text-[#b8020a] font-semibold mb-6">
                  {result.analysis.overview?.three_word_summary}
                </p>

                <h3 className="font-semibold mb-2">Ratings</h3>
                <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                  {result.analysis.ratings && Object.entries(result.analysis.ratings).map(([key, value]) => (
                    <div key={key}>
                      <span className="capitalize">{key.replace('_', ' ')}: </span>
                      <span className="font-semibold">{value.score}/5</span>
                    </div>
                  ))}
                </div>

                {result.transport && (
                  <div className="border-t-2 border-gray-200 pt-6">
                    <h3 className="font-semibold mb-3">Transport & Connectivity</h3>

                    <div className="mb-4">
                      <p className="text-sm mb-2">
                        <span className="font-semibold">Connectivity Score: </span>
                        <span className="text-[#b8020a]">{result.transport.connectivity_score}/5</span>
                      </p>
                    </div>

                    <h4 className="font-semibold text-sm mb-2">Travel Times to Landmarks</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {result.transport.landmark_travel_times?.map((landmark, idx) => (
                        <div key={idx} className="flex justify-between">
                          <span>{landmark.landmark}:</span>
                          <span className="font-medium">{landmark.time}</span>
                        </div>
                      ))}
                    </div>

                    {result.transport.nearby_stations && result.transport.nearby_stations.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-semibold text-sm mb-2">Nearby Stations</h4>
                        <div className="text-sm">
                          {result.transport.nearby_stations.slice(0, 5).map((station, idx) => (
                            <div key={idx} className="mb-1">
                              <span className="font-medium">{station.name}</span>
                              <span className="text-gray-600"> - {station.walk_time_minutes} min walk</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
