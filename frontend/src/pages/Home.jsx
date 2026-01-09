import { useState } from 'react';

function Home() {
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!address.trim()) return;

    setLoading(true);
    // TODO: call API to analyze address
    console.log('Analyzing:', address);
    setTimeout(() => setLoading(false), 2000);
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
      </div>
    </div>
  );
}

export default Home;
