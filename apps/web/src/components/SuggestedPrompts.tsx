import React from 'react';
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { 
  Building2, 
  TrendingUp, 
  Users, 
  Lightbulb,
  MessageCircle
} from "lucide-react";

interface SuggestedPromptsProps {
  onPromptClick: (prompt: string) => void;
}

const suggestedPrompts = [
  {
    icon: Building2,
    title: "Tech Startup Grants",
    prompt: "What grants are available for a tech startup with 15 employees in Kuala Lumpur?",
    category: "Technology"
  },
  {
    icon: TrendingUp,
    title: "Digital Transformation",
    prompt: "Show me digital transformation grants for SMEs with annual revenue under RM5 million",
    category: "Digital"
  },
  {
    icon: Users,
    title: "Women-Led Business",
    prompt: "What funding opportunities are available for women-led businesses in Malaysia?",
    category: "Women Entrepreneurs"
  },
  {
    icon: Lightbulb,
    title: "R&D Funding",
    prompt: "What research and development grants can help fund my innovative project?",
    category: "Innovation"
  }
];

export default function SuggestedPrompts({ onPromptClick }: SuggestedPromptsProps) {
  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          Quick Start Prompts
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {suggestedPrompts.map((prompt, index) => (
            <Button
              key={index}
              variant="outline"
              className="h-auto p-4 text-left flex flex-col items-start gap-2 hover:bg-blue-50 hover:border-blue-200"
              onClick={() => onPromptClick(prompt.prompt)}
            >
              <div className="flex items-center gap-2 w-full">
                <prompt.icon className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-sm">{prompt.title}</span>
                <span className="ml-auto text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                  {prompt.category}
                </span>
              </div>
              <span className="text-xs text-muted-foreground text-left">
                {prompt.prompt}
              </span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}