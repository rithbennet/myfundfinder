import React from 'react';
import { Badge } from "~/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { 
  CheckCircle, 
  ExternalLink, 
  BookOpen, 
  Target,
  DollarSign,
  Calendar,
  Users
} from "lucide-react";

interface ChatbotResponseProps {
  response: string;
  sources?: string[];
  sessionId?: string;
}

interface Grant {
  title: string;
  content: string;
  amount?: string;
  eligibility?: string;
  deadline?: string;
}

export default function ChatbotResponse({ response, sources, sessionId }: ChatbotResponseProps) {
  // Function to format the response text into structured content
  const formatResponse = (text: string) => {
    // Split by numbered items (1. 2. 3. etc.)
    const sections = text.split(/(?=\d+\.\s)/);
    const intro = sections[0];
    const recommendations = sections.slice(1);

    return {
      intro: intro.trim(),
      recommendations: recommendations.map(section => {
        const lines = section.split('\n').filter(line => line.trim());
        const title = lines[0]?.replace(/^\d+\.\s*/, '') || '';
        const content = lines.slice(1).join('\n').trim();
        
        // Extract key information
        const amountMatch = content.match(/up to RM?([\d,]+)/i);
        const eligibilityMatch = content.match(/eligible.*?(?=\.|$)/i);
        const deadlineMatch = content.match(/deadline.*?(?=\.|$)/i);
        
        return { 
          title, 
          content,
          amount: amountMatch ? `RM${amountMatch[1]}` : null,
          eligibility: eligibilityMatch ? eligibilityMatch[0] : null,
          deadline: deadlineMatch ? deadlineMatch[0] : null
        };
      })
    };
  };

  const { intro, recommendations } = formatResponse(response);

  const handleApplyForGrant = (grantTitle: string) => {
    // Navigate to application or external link
    console.log(`Applying for: ${grantTitle}`);
    // You can add actual navigation logic here
  };

  const handleSaveRecommendations = () => {
    // Save to user's profile or local storage
    const data = {
      sessionId,
      recommendations: recommendations.map(r => r.title),
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('saved_grant_recommendations', JSON.stringify(data));
    console.log('Recommendations saved:', data);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Target className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-xl">Grant Recommendations</CardTitle>
              <p className="text-sm text-muted-foreground">AI-powered funding suggestions for your company</p>
            </div>
          </div>
        </CardHeader>

        {/* Introduction */}
        {intro && (
          <CardContent>
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
              <p className="text-gray-700 leading-relaxed">{intro}</p>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Recommendations Grid */}
      {recommendations.length > 0 && (
        <div className="grid gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-600" />
              Available Grants ({recommendations.length})
            </h3>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleSaveRecommendations}
              className="flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Save All
            </Button>
          </div>
          
          {recommendations.map((grant, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-green-600 font-semibold text-sm">{index + 1}</span>
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{grant.title}</CardTitle>
                      
                      {/* Quick Info Tags */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {grant.amount && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <DollarSign className="w-3 h-3" />
                            {grant.amount}
                          </Badge>
                        )}
                        {grant.deadline && (
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            Deadline Info Available
                          </Badge>
                        )}
                        {grant.eligibility && (
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            Eligibility Criteria
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="text-sm text-gray-600 leading-relaxed whitespace-pre-line mb-4">
                  {grant.content}
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-2 pt-2 border-t">
                  <Button 
                    size="sm" 
                    onClick={() => handleApplyForGrant(grant.title)}
                    className="flex items-center gap-2"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Learn More
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      const data = { title: grant.title, content: grant.content, timestamp: new Date().toISOString() };
                      localStorage.setItem(`saved_grant_${index}`, JSON.stringify(data));
                    }}
                  >
                    Save Grant
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Sources */}
      {sources && sources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Information Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {[...new Set(sources)].map((source, index) => (
                <Badge
                  key={index}
                  variant="outline"
                  className="text-xs"
                >
                  {source}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Summary */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">Next Steps</h3>
              <p className="text-sm text-blue-700">
                Review these {recommendations.length} grant opportunities and start your applications
              </p>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="default"
                size="sm"
                onClick={() => {
                  // Navigate to applications or external grants portal
                  window.open('https://www.smebank.com.my/grants', '_blank');
                }}
              >
                View All Grants
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}