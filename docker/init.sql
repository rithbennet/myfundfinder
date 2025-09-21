-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Sample grant data for testing
CREATE TABLE IF NOT EXISTS sample_grants (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    url VARCHAR(500),
    sector VARCHAR(100),
    deadline DATE,
    amount VARCHAR(100),
    eligibility TEXT,
    provider VARCHAR(200),
    embedding vector(1536), -- Titan embeddings are 1536 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample grant data
INSERT INTO sample_grants (title, description, url, sector, amount, eligibility, provider) VALUES
('Small Business Innovation Grant', 'Funding for innovative small businesses developing new technologies and solutions. Supports R&D activities, prototype development, and market validation.', 'https://example.gov/sbir', 'Technology', '$50,000 - $500,000', 'Small businesses with fewer than 500 employees, focus on innovation and technology development', 'Government - Department of Commerce'),
('Green Energy Startup Fund', 'Investment fund specifically for renewable energy startups and clean technology companies. Focuses on solar, wind, and battery storage innovations.', 'https://example.com/green-fund', 'Renewable Energy', '$100,000 - $2,000,000', 'Startups and SMEs in renewable energy sector, must demonstrate environmental impact', 'Corporate - GreenTech Ventures'),
('Agriculture Modernization Grant', 'Support for agricultural businesses adopting modern farming techniques, sustainable practices, and digital agriculture solutions.', 'https://example.gov/agri-grant', 'Agriculture', '$25,000 - $300,000', 'Agricultural businesses, cooperatives, and agtech startups', 'Government - Department of Agriculture'),
('Healthcare Innovation Fund', 'Funding for healthcare technology companies developing digital health solutions, medical devices, and telehealth platforms.', 'https://example.com/health-fund', 'Healthcare', '$75,000 - $1,500,000', 'Healthcare startups and established companies with innovative solutions', 'Corporate - HealthTech Partners'),
('Manufacturing Excellence Grant', 'Support for manufacturing companies implementing Industry 4.0 technologies, automation, and efficiency improvements.', 'https://example.gov/manufacturing', 'Manufacturing', '$100,000 - $750,000', 'Manufacturing companies looking to modernize operations and improve efficiency', 'Government - Economic Development Agency'),
('Retail Digital Transformation Fund', 'Investment for retail businesses adopting e-commerce, digital marketing, and customer experience technologies.', 'https://example.com/retail-fund', 'Retail', '$30,000 - $400,000', 'Retail businesses transitioning to digital channels and improving customer experience', 'Corporate - Retail Innovation Group'),
('Education Technology Grant', 'Funding for companies developing educational software, learning management systems, and digital learning tools.', 'https://example.gov/edtech', 'Education', '$40,000 - $600,000', 'EdTech startups and companies serving educational institutions', 'Government - Education Department'),
('Financial Services Innovation Fund', 'Support for fintech companies developing payment solutions, lending platforms, and financial management tools.', 'https://example.com/fintech-fund', 'Financial Services', '$150,000 - $2,500,000', 'Fintech startups and established financial service providers with innovative solutions', 'Corporate - Financial Innovation Labs');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_grants_sector ON sample_grants(sector);
CREATE INDEX IF NOT EXISTS idx_grants_deadline ON sample_grants(deadline);
CREATE INDEX IF NOT EXISTS idx_grants_provider ON sample_grants(provider);