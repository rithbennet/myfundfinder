"use client";

import { ChatInterface } from "@/feature/chat";
import { useEffect, useState } from "react";
import { isAuthenticated } from "@/lib/auth";

export default function ChatTestPage() {
  const [isAuth, setIsAuth] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setIsAuth(isAuthenticated());
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!isAuth) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Chat Test</h1>
        <p>Please sign in to use the chat feature.</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Chat Test</h1>
      <ChatInterface />
    </div>
  );
}
