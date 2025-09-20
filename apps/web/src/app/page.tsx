"use client";

import { useState } from "react";

interface CompanyProfile {
  sector: string;
  size: string;
  region?: string;
  keywords?: string;
}

interface Grant {
  id: string;
  title: string;
  description?: string;
  url: string;
  sector?: string;
  amount?: string;
  provider?: string;
  ai_explanation?: string;
}

export default function HomePage() {
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile>({
    sector: "",
    size: "",
    region: "",
    keywords: ""
  });
  const [aiAnalysis, setAiAnalysis] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<Grant[]>([]);
  const [chatMessage, setChatMessage] = useState<string>("");
  const [chatResponse, setChatResponse] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const analyzeCompany = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/ai/analyze-company", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(companyProfile),
      });
      const data = await response.json();
      setAiAnalysis(data.analysis);
    } catch (error) {
      console.error("Error analyzing company:", error);
    }
    setLoading(false);
  };

  const searchFunds = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/ai/search-funds", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          company_profile: companyProfile,
        }),
      });
      const data = await response.json();
      setSearchResults(data.funds || []);
    } catch (error) {
      console.error("Error searching funds:", error);
    }
    setLoading(false);
  };

  const chatWithAI = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: chatMessage,
          company_profile: companyProfile,
        }),
      });
      const data = await response.json();
      setChatResponse(data.response);
    } catch (error) {
      console.error("Error chatting with AI:", error);
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-[#2e026d] to-[#15162c] text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-5xl font-extrabold text-center mb-8 text-[hsl(280,100%,70%)]">
          💰 MyFundFinder
        </h1>
        <p className="text-center text-xl mb-12">AI-Powered SME Fund Discovery Platform</p>

        {/* Company Profile Section */}
        <div className="bg-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Company Profile</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Sector</label>
              <select
                value={companyProfile.sector}
                onChange={(e) => setCompanyProfile({...companyProfile, sector: e.target.value})}
                className="w-full p-2 rounded bg-white/20 text-white"
              >
                <option value="">Select Sector</option>
                <option value="Technology">Technology</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Retail">Retail</option>
                <option value="Agriculture">Agriculture</option>
                <option value="Renewable Energy">Renewable Energy</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Education">Education</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Company Size</label>
              <select
                value={companyProfile.size}
                onChange={(e) => setCompanyProfile({...companyProfile, size: e.target.value})}
                className="w-full p-2 rounded bg-white/20 text-white"
              >
                <option value="">Select Size</option>
                <option value="Startup (1-10 employees)">Startup (1-10 employees)</option>
                <option value="Small (11-50 employees)">Small (11-50 employees)</option>
                <option value="Medium (51-250 employees)">Medium (51-250 employees)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Region</label>
              <input
                type="text"
                value={companyProfile.region}
                onChange={(e) => setCompanyProfile({...companyProfile, region: e.target.value})}
                placeholder="e.g., North America, Europe, Asia"
                className="w-full p-2 rounded bg-white/20 text-white placeholder-gray-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Keywords/Focus Areas</label>
              <input
                type="text"
                value={companyProfile.keywords}
                onChange={(e) => setCompanyProfile({...companyProfile, keywords: e.target.value})}
                placeholder="e.g., AI, sustainability, innovation"
                className="w-full p-2 rounded bg-white/20 text-white placeholder-gray-300"
              />
            </div>
          </div>
          <button
            onClick={analyzeCompany}
            disabled={loading || !companyProfile.sector || !companyProfile.size}
            className="mt-4 bg-[hsl(280,100%,70%)] text-white px-6 py-2 rounded-lg hover:bg-[hsl(280,100%,60%)] disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Get AI Funding Recommendations"}
          </button>
        </div>

        {/* AI Analysis Results */}
        {aiAnalysis && (
          <div className="bg-white/10 rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">AI Funding Analysis</h2>
            <div className="whitespace-pre-wrap text-gray-100">{aiAnalysis}</div>
          </div>
        )}

        {/* Fund Search Section */}
        <div className="bg-white/10 rounded-xl p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Search Funds</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for funding opportunities..."
              className="flex-1 p-2 rounded bg-white/20 text-white placeholder-gray-300"
            />
            <button
              onClick={searchFunds}
              disabled={loading || !searchQuery}
              className="bg-[hsl(280,100%,70%)] text-white px-6 py-2 rounded-lg hover:bg-[hsl(280,100%,60%)] disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="bg-white/10 rounded-xl p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Funding Opportunities</h2>
            <div className="space-y-4">
              {searchResults.map((grant) => (
                <div key={grant.id} className="bg-white/20 rounded-lg p-4">
                  <h3 className="text-xl font-semibold mb-2">{grant.title}</h3>
                  <p className="text-gray-200 mb-2">{grant.description}</p>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {grant.sector && (
                      <span className="bg-blue-500 px-2 py-1 rounded text-sm">
                        {grant.sector}
                      </span>
                    )}
                    {grant.amount && (
                      <span className="bg-green-500 px-2 py-1 rounded text-sm">
                        {grant.amount}
                      </span>
                    )}
                    {grant.provider && (
                      <span className="bg-purple-500 px-2 py-1 rounded text-sm">
                        {grant.provider}
                      </span>
                    )}
                  </div>
                  {grant.ai_explanation && (
                    <div className="bg-yellow-500/20 p-3 rounded mt-2">
                      <strong>AI Recommendation:</strong> {grant.ai_explanation}
                    </div>
                  )}
                  <a
                    href={grant.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[hsl(280,100%,70%)] hover:underline"
                  >
                    Learn More →
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Chat Section */}
        <div className="bg-white/10 rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-4">Chat with AI Funding Assistant</h2>
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Ask me anything about funding opportunities..."
              className="flex-1 p-2 rounded bg-white/20 text-white placeholder-gray-300"
            />
            <button
              onClick={chatWithAI}
              disabled={loading || !chatMessage}
              className="bg-[hsl(280,100%,70%)] text-white px-6 py-2 rounded-lg hover:bg-[hsl(280,100%,60%)] disabled:opacity-50"
            >
              {loading ? "Thinking..." : "Ask AI"}
            </button>
          </div>
          {chatResponse && (
            <div className="bg-white/20 rounded-lg p-4">
              <h3 className="font-semibold mb-2">AI Assistant:</h3>
              <div className="whitespace-pre-wrap text-gray-100">{chatResponse}</div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
