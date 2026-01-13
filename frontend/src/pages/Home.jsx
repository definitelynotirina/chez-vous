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
    <div className="min-h-screen flex flex-col items-center justify-center px-4 relative">
      {/* Corner logo - only show when no results */}
      {!result && (
        <img
          src="/chez_stamp.png"
          alt="Chez-Vous"
          className="absolute top-4 left-4 w-20 h-20 opacity-80"
        />
      )}

      <div className="max-w-4xl w-full">
        {/* Show search form only when no results */}
        {!result && (
          <div className="text-center">
            {/* Logo text */}
            <img
              src="/chez_text.png"
              alt="Chez-Vous"
              className="mx-auto mb-12 h-24 w-auto"
            />

            {loading ? (
              <div className="flex flex-col items-center">
                <img
                  src="/eiffel.gif"
                  alt="Loading..."
                  className="w-32 h-32 mb-4"
                />
                <p className="text-sm text-[#340a10]">Analyzing your neighborhood...</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="w-full">
                <div className="relative">
                  <input
                    type="text"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="Enter a Paris address..."
                    className="w-full px-6 py-4 text-lg border border-[#340a10] border-opacity-20 rounded-full focus:outline-none focus:border-[#340a10] focus:border-opacity-40 transition-colors text-[#340a10] placeholder:text-[#340a10] placeholder:opacity-50"
                  />
                </div>

                <button
                  type="submit"
                  onClick={(e) => {
                    if (!address.trim()) {
                      e.preventDefault();
                    }
                  }}
                  className="mt-6 px-8 py-3 bg-[#340a10] text-[#e9e9e6] hover:bg-[#4a0e16] transition-colors font-medium rounded-full cursor-pointer"
                >
                  Search
                </button>
              </form>
            )}
          </div>
        )}

        {error && (
          <div className="mt-8 p-4 border-2 border-[#340a10] text-[#340a10]">
            {error}
          </div>
        )}

        {result && (
          <div className="py-12 text-left">
            {/* Icon at top */}
            <div className="flex justify-center mb-8">
              <img
                src="/chez_stamp.png"
                alt="Chez-Vous"
                className="w-20 h-20 opacity-80"
              />
            </div>

            {/* Arrondissement & Address */}
            <div className="mb-12 flex items-start justify-between gap-8">
              <div className="flex flex-col items-start">
                <h2 className="heading-font text-5xl text-[#b8020a] mb-4">Arrondissement</h2>
                {result.geo_data?.arrondissement && (
                  <img
                    src={`/arr_numbers/${result.geo_data.arrondissement}.png`}
                    alt={`${result.geo_data.arrondissement}e arrondissement`}
                    className="h-64"
                  />
                )}
              </div>
              <div className="flex-1 flex flex-col items-end">
                <div className="w-full mb-6">
                  <h3 className="text-xl text-[#340a10] font-semibold mb-3">Full address</h3>
                  <p className="text-sm text-[#340a10]">{result.geo_data?.full_address}</p>
                </div>

                {result.analysis && (
                  <div className="w-full">
                    <h3 className="text-xl text-[#340a10] font-semibold mb-3">Neighborhood Character</h3>
                    <p className="text-sm text-[#340a10]">{result.analysis.overview?.description}</p>
                    <p className="heading-font text-4xl text-[#b8020a] tracking-[0.2em] mt-6 text-center capitalize">
                      {result.analysis.overview?.three_word_summary}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Separator */}
            <div className="border-t border-[#340a10] opacity-30 my-12"></div>

            {/* Word of Mouth */}
            {result.analysis && result.analysis.what_locals_say && (
              <div className="mb-12">
                <h3 className="text-3xl text-[#340a10] font-bold mb-2">Word of Mouth</h3>
                <p className="text-sm text-[#340a10] mb-6 opacity-70">What Reddit is saying</p>
                <div className="space-y-4 text-sm text-[#340a10]">
                  {Array.isArray(result.analysis.what_locals_say) ? (
                    result.analysis.what_locals_say.map((paragraph, idx) => (
                      <p key={idx}>{paragraph}</p>
                    ))
                  ) : (
                    <p>{result.analysis.what_locals_say}</p>
                  )}
                </div>
              </div>
            )}

            {/* Separator */}
            <div className="border-t border-[#340a10] opacity-30 my-12"></div>

            {/* Ratings */}
            {result.analysis && (
              <div className="mb-12">
                <div className="grid grid-cols-4 gap-4">
                  {result.analysis.ratings && Object.entries(result.analysis.ratings).map(([key, value]) => (
                    <div key={key} className="text-center">
                      <p className="capitalize text-lg text-[#b8020a] font-semibold mb-2">{key.replace('_', ' ')}</p>
                      <img
                        src={`/${value.score}_5.png`}
                        alt={`${value.score} out of 5`}
                        className="mx-auto h-12"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Separator */}
            <div className="border-t border-[#340a10] opacity-30 my-12"></div>

            {/* Transport */}
            {result.transport && (
              <div className="mb-12">
                {/* Travel Times to Landmarks */}
                {result.transport.landmark_travel_times && (
                  <div className="mb-12">
                    <h3 className="text-3xl text-[#340a10] font-bold mb-2">Travel Times to Landmarks</h3>
                    <p className="text-sm text-[#340a10] mb-6 opacity-70">Public transport from your address</p>
                    <div className="grid grid-cols-6 gap-6">
                      {result.transport.landmark_travel_times.map((landmark, idx) => {
                        const iconMap = {
                          'Sacré-Cœur': 'sacre',
                          'Notre-Dame': 'notre',
                          'Eiffel Tower': 'eiffel',
                          'Arc de Triomphe': 'arc',
                          'Louvre': 'louvre',
                          'Champs-Élysées': 'champs'
                        };
                        const iconName = iconMap[landmark.landmark];
                        const displayName = landmark.landmark;
                        return (
                          <div key={idx} className="flex flex-col items-center">
                            <p className="text-xs text-[#340a10] text-center mb-2 font-medium">{displayName}</p>
                            <img
                              src={`/landmarks/${iconName}.png`}
                              alt={landmark.landmark}
                              className="h-16 w-16 mb-3"
                            />
                            <p className="text-sm text-[#340a10] text-center font-semibold">{landmark.time}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Nearby Stations */}
                {result.transport.nearby_stations && result.transport.nearby_stations.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-3xl text-[#340a10] font-bold mb-2">Nearby Stations</h3>
                    <p className="text-sm text-[#340a10] mb-6 opacity-70">Within walking distance</p>
                    <div className="space-y-3">
                      {result.transport.nearby_stations.slice(0, 5).map((station, idx) => (
                        <div key={idx} className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-sm text-[#340a10]">{station.name}</p>
                            <p className="text-xs text-[#340a10] mt-1 opacity-70">
                              {station.transport_type}
                              {station.lines && station.lines.length > 0 && (
                                <span> • Lines: {station.lines.join(', ')}</span>
                              )}
                            </p>
                          </div>
                          <span className="text-sm text-[#340a10] whitespace-nowrap ml-4 font-semibold">
                            {station.walk_time_minutes} min walk
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-center mt-12">
              <button
                onClick={() => {
                  setResult(null);
                  setAddress('');
                  setError(null);
                }}
                className="px-8 py-3 bg-[#340a10] text-[#e9e9e6] hover:bg-[#4a0e16] transition-colors font-medium rounded-full"
              >
                Search Another Address
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;
