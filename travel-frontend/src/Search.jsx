import React, { useState } from "react";

const Search = () => {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("general"); // hotel | flight | general
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      let endpoint = "http://localhost:5000/search"; // default general

      if (category === "hotel") {
        endpoint = "http://localhost:5000/hotel";
      } else if (category === "flight") {
        endpoint = "http://localhost:5000/flight";
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      console.log(data);

      if (data.error) {
        setResults([data.error]);
      } else {
        setResults(data.results || []);
      }
    } catch (error) {
      console.error("Error fetching:", error);
      setResults(["Something went wrong!"]);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-purple-600 to-blue-500 p-6 text-white">
      <h1 className="text-3xl font-bold mb-6">🌍 Travel Planner</h1>

      <div className="flex gap-4 mb-4">
        <input
          type="text"
          value={query}
          placeholder="Search hotels, flights, or anything..."
          onChange={(e) => setQuery(e.target.value)}
          className="px-4 py-2 rounded-lg text-black w-80"
        />

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-3 py-2 rounded-lg text-black"
        >
          <option value="general">General</option>
          <option value="hotel">Hotel</option>
          <option value="flight">Flight</option>
        </select>

        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-yellow-400 text-black font-bold rounded-lg hover:bg-yellow-300"
        >
          Search
        </button>
      </div>

      <div className="bg-white text-black rounded-lg shadow-md p-4 w-[600px] max-h-[400px] overflow-y-auto">
        <h2 className="text-xl font-semibold mb-3">Results:</h2>
        <ul className="list-disc pl-5 space-y-2">
          {results.length > 0 ? (
            results.map((item, idx) => (
              <li key={idx}>
                <a
                  href={item}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  {item}
                </a>
              </li>
            ))
          ) : (
            <p>No results yet...</p>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Search;
