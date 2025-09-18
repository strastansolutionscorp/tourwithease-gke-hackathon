import AIChat from "@/components/AIChat";
import { Metadata } from "next";

// Metadata for SEO
export const metadata: Metadata = {
  title: "AI Travel Assistant - TourWithEase",
  description:
    "Chat with our AI travel assistant to plan your perfect trip, find flights, hotels, and get personalized travel recommendations.",
  keywords:
    "AI travel assistant, flight search, hotel booking, travel planning, GKE hackathon",
};

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Main Chat Container */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="h-[80vh]">
              <AIChat conversationId="demo-chat" className="h-full" />
            </div>
          </div>

          {/* Demo Info */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-sm font-medium text-blue-800 mb-2">
              🤖 TourWithEase AI Demo - GKE Hackathon 2024
            </h3>
            <p className="text-sm text-blue-600 mb-3">
              This AI assistant uses multi-agent architecture with ADK + A2A
              protocol running on Google Kubernetes Engine.
            </p>

            {/* Status Report */}
            <div className="mb-3">
              <h4 className="text-xs font-semibold text-blue-800 mb-2">
                📊 STATUS REPORT
              </h4>
              <div className="text-xs text-blue-600 space-y-1">
                <div>✅ COMPLETED - Core chat functionality</div>
                <div>🔄 PARTIALLY IMPLEMENTED - Advanced search features</div>
                <div>⏳ NOT STARTED - Booking integration</div>
              </div>
            </div>

            {/* Quick Examples */}
            <div>
              <h4 className="text-xs font-semibold text-blue-800 mb-2">
                💡 Try asking:
              </h4>
              <div className="text-xs text-blue-600">
                <div>"Plan a romantic trip to Paris next week"</div>
                <div>"Find flights from NYC to London"</div>
                <div>"Recommend hotels in Tokyo under $200/night"</div>
              </div>
            </div>
          </div>

          {/* Additional Features Info */}
          <div className="mt-4 p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-xs font-medium text-green-800">
                Live Features
              </span>
            </div>
            <div className="text-xs text-green-600 space-y-1">
              <div>🔍 Real-time flight & hotel search</div>
              <div>💬 WebSocket-powered live chat</div>
              <div>🎯 Multi-agent AI recommendations</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
