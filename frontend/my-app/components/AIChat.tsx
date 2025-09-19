// "use client";
// import { Bot, Hotel, Loader2, MapPin, Plane, Send, User } from "lucide-react";
// import React, { useEffect, useRef, useState } from "react";

// interface Message {
//   id: string;
//   role: "user" | "assistant";
//   content: string;
//   timestamp: string; // ISO string for better serialization
//   status?: "sending" | "sent" | "error";
//   results?: any;
//   next_actions?: string[];
// }

// interface AIChatProps {
//   conversationId?: string;
//   className?: string;
// }

// const AIChat: React.FC<AIChatProps> = ({
//   conversationId = "default",
//   className = "",
// }) => {
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [input, setInput] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [isConnected, setIsConnected] = useState(false);
//   const messagesEndRef = useRef<HTMLDivElement>(null);
//   const wsRef = useRef<WebSocket | null>(null);
//   const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

//   const API_BASE_URL =
//     process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

//   // More robust WebSocket URL construction
//   const getWebSocketUrl = (baseUrl: string) => {
//     if (baseUrl.startsWith("https://")) {
//       return baseUrl.replace("https://", "wss://");
//     }
//     return baseUrl.replace("http://", "ws://");
//   };

//   const WS_URL = `${getWebSocketUrl(API_BASE_URL)}/ws/${conversationId}`;

//   useEffect(() => {
//     // Initialize WebSocket connection
//     initializeWebSocket();

//     // Add welcome message with ISO timestamp
//     setMessages([
//       {
//         id: "welcome",
//         role: "assistant",
//         content:
//           "Hi! I'm your AI travel assistant. I can help you search for flights, find hotels, and plan amazing trips. What would you like to explore today?",
//         timestamp: new Date().toISOString(),
//       },
//     ]);

//     return () => {
//       if (wsRef.current) {
//         wsRef.current.close();
//       }
//       if (reconnectTimeout.current) {
//         clearTimeout(reconnectTimeout.current);
//       }
//     };
//   }, [conversationId]);

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const initializeWebSocket = () => {
//     try {
//       wsRef.current = new WebSocket(WS_URL);

//       wsRef.current.onopen = () => {
//         setIsConnected(true);
//         console.log("WebSocket connected");
//       };

//       wsRef.current.onmessage = (event) => {
//         const data = JSON.parse(event.data);
//         if (data.type === "chat_response") {
//           handleWebSocketMessage(data.data);
//         }
//       };

//       wsRef.current.onclose = () => {
//         setIsConnected(false);
//         console.log("WebSocket disconnected");

//         // Clear any existing timeout
//         if (reconnectTimeout.current) {
//           clearTimeout(reconnectTimeout.current);
//         }

//         // Attempt to reconnect after 3 seconds
//         reconnectTimeout.current = setTimeout(() => {
//           if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
//             initializeWebSocket();
//           }
//         }, 3000);
//       };

//       wsRef.current.onerror = (error) => {
//         console.error("WebSocket error:", error);
//         setIsConnected(false);
//       };
//     } catch (error) {
//       console.error("Failed to initialize WebSocket:", error);
//     }
//   };

//   const handleWebSocketMessage = (data: any) => {
//     // Handle real-time updates from WebSocket
//     console.log("WebSocket message:", data);
//   };

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   const sendMessage = async () => {
//     if (!input.trim() || isLoading) return;

//     const userMessage: Message = {
//       id: `user-${Date.now()}`,
//       role: "user",
//       content: input,
//       timestamp: new Date().toISOString(),
//       status: "sending",
//     };

//     setMessages((prev) => [...prev, userMessage]);
//     const currentInput = input;
//     setInput("");
//     setIsLoading(true);

//     try {
//       const response = await fetch(`${API_BASE_URL}/chat`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           // Add authorization header if needed
//           // 'Authorization': `Bearer ${token}`
//         },
//         body: JSON.stringify({
//           message: currentInput,
//           conversation_id: conversationId,
//           user_context: {},
//         }),
//       });

//       if (!response.ok) {
//         throw new Error(`Failed to send message: ${response.status}`);
//       }

//       const data = await response.json();

//       // Update user message status
//       setMessages((prev) =>
//         prev.map((msg) =>
//           msg.id === userMessage.id ? { ...msg, status: "sent" } : msg
//         )
//       );

//       // Add assistant response
//       const assistantMessage: Message = {
//         id: `assistant-${Date.now()}`,
//         role: "assistant",
//         content: data.message,
//         timestamp: data.timestamp
//           ? new Date(data.timestamp).toISOString()
//           : new Date().toISOString(),
//         results: data.results,
//         next_actions: data.next_actions,
//       };

//       setMessages((prev) => [...prev, assistantMessage]);
//     } catch (error) {
//       console.error("Error sending message:", error);

//       // Update user message status to error
//       setMessages((prev) =>
//         prev.map((msg) =>
//           msg.id === userMessage.id ? { ...msg, status: "error" } : msg
//         )
//       );

//       // Add error message
//       const errorMessage: Message = {
//         id: `error-${Date.now()}`,
//         role: "assistant",
//         content: "I'm sorry, I encountered an error. Please try again.",
//         timestamp: new Date().toISOString(),
//       };

//       setMessages((prev) => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   };

//   const renderMessage = (message: Message) => {
//     const isUser = message.role === "user";

//     return (
//       <div
//         key={message.id}
//         className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
//       >
//         <div
//           className={`flex max-w-3xl ${isUser ? "flex-row-reverse" : "flex-row"}`}
//         >
//           {/* Avatar */}
//           <div className={`flex-shrink-0 ${isUser ? "ml-3" : "mr-3"}`}>
//             <div
//               className={`w-8 h-8 rounded-full flex items-center justify-center ${
//                 isUser ? "bg-blue-500" : "bg-green-500"
//               }`}
//             >
//               {isUser ? (
//                 <User className="w-4 h-4 text-white" />
//               ) : (
//                 <Bot className="w-4 h-4 text-white" />
//               )}
//             </div>
//           </div>

//           {/* Message Content */}
//           <div className={`flex-1 ${isUser ? "text-right" : "text-left"}`}>
//             <div
//               className={`inline-block p-3 rounded-lg ${
//                 isUser
//                   ? "bg-blue-500 text-white rounded-br-none"
//                   : "bg-gray-100 text-gray-800 rounded-bl-none"
//               }`}
//             >
//               <p className="whitespace-pre-wrap">{message.content}</p>

//               {message.status === "sending" && (
//                 <div className="flex items-center justify-end mt-1">
//                   <Loader2 className="w-3 h-3 animate-spin" />
//                 </div>
//               )}

//               {message.status === "error" && (
//                 <div className="text-red-300 text-xs mt-1">Failed to send</div>
//               )}
//             </div>

//             {/* Results Display */}
//             {message.results && (
//               <div className="mt-3 space-y-2">
//                 {message.results.flights && (
//                   <ResultCard
//                     title="Flight Options"
//                     icon={<Plane className="w-4 h-4" />}
//                     data={message.results.flights}
//                     type="flights"
//                   />
//                 )}
//                 {message.results.hotels && (
//                   <ResultCard
//                     title="Hotel Options"
//                     icon={<Hotel className="w-4 h-4" />}
//                     data={message.results.hotels}
//                     type="hotels"
//                   />
//                 )}
//                 {message.results.context && (
//                   <ResultCard
//                     title="Travel Context"
//                     icon={<MapPin className="w-4 h-4" />}
//                     data={message.results.context}
//                     type="context"
//                   />
//                 )}
//               </div>
//             )}

//             {/* Next Actions */}
//             {message.next_actions && message.next_actions.length > 0 && (
//               <div className="mt-2 flex flex-wrap gap-2">
//                 {message.next_actions.map((action, index) => (
//                   <button
//                     key={index}
//                     onClick={() => setInput(action)}
//                     className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full hover:bg-blue-200 transition-colors"
//                   >
//                     {action}
//                   </button>
//                 ))}
//               </div>
//             )}

//             <div className="text-xs text-gray-400 mt-1">
//               {new Date(message.timestamp).toLocaleTimeString()}
//             </div>
//           </div>
//         </div>
//       </div>
//     );
//   };

//   return (
//     <div className={`flex flex-col h-full bg-white ${className}`}>
//       {/* Header */}
//       <div className="flex items-center justify-between p-4 border-b bg-gray-50">
//         <h2 className="text-lg font-semibold text-gray-800">
//           AI Travel Assistant
//         </h2>
//         <div className="flex items-center space-x-2">
//           <div
//             className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"}`}
//           ></div>
//           <span className="text-xs text-gray-500">
//             {isConnected ? "Connected" : "Connecting..."}
//           </span>
//         </div>
//       </div>

//       {/* Messages */}
//       <div className="flex-1 overflow-y-auto p-4 space-y-4">
//         {messages.map(renderMessage)}

//         {isLoading && (
//           <div className="flex justify-start">
//             <div className="flex items-center space-x-2 p-3 bg-gray-100 rounded-lg">
//               <Loader2 className="w-4 h-4 animate-spin" />
//               <span className="text-sm text-gray-600">Thinking...</span>
//             </div>
//           </div>
//         )}

//         <div ref={messagesEndRef} />
//       </div>

//       {/* Input */}
//       <div className="p-4 border-t bg-gray-50">
//         <div className="flex items-end space-x-2">
//           <div className="flex-1">
//             <textarea
//               value={input}
//               onChange={(e) => setInput(e.target.value)}
//               onKeyDown={handleKeyDown}
//               placeholder="Ask me about flights, hotels, or travel planning..."
//               className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
//               rows={1}
//               disabled={isLoading}
//             />
//           </div>
//           <button
//             onClick={sendMessage}
//             disabled={!input.trim() || isLoading}
//             className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
//           >
//             <Send className="w-4 h-4" />
//           </button>
//         </div>

//         {/* Quick Actions */}
//         <div className="flex flex-wrap gap-2 mt-2">
//           {[
//             "Search flights to Paris",
//             "Find hotels in London",
//             "Plan a romantic getaway",
//           ].map((suggestion, index) => (
//             <button
//               key={index}
//               onClick={() => setInput(suggestion)}
//               className="text-xs px-3 py-1 bg-gray-200 text-gray-600 rounded-full hover:bg-gray-300 transition-colors"
//             >
//               {suggestion}
//             </button>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// };

// // Result Card Component
// interface ResultCardProps {
//   title: string;
//   icon: React.ReactNode;
//   data: any;
//   type: "flights" | "hotels" | "context";
// }

// const ResultCard: React.FC<ResultCardProps> = ({ title, icon, data, type }) => {
//   const [isExpanded, setIsExpanded] = useState(false);

//   const renderContent = () => {
//     if (type === "flights" && Array.isArray(data)) {
//       return (
//         <div className="space-y-2">
//           {data
//             .slice(0, isExpanded ? data.length : 3)
//             .map((flight: any, index: number) => (
//               <div
//                 key={index}
//                 className="p-2 bg-gray-50 rounded border-l-4 border-blue-400"
//               >
//                 <div className="flex justify-between items-start">
//                   <div>
//                     <div className="font-medium">
//                       {flight.airline || "Airline"}
//                     </div>
//                     <div className="text-sm text-gray-600">
//                       {flight.departure_time || "Departure"} -{" "}
//                       {flight.arrival_time || "Arrival"}
//                     </div>
//                     <div className="text-sm text-gray-500">
//                       {flight.duration || "Duration"} •{" "}
//                       {flight.stops === 0
//                         ? "Non-stop"
//                         : `${flight.stops} stops`}
//                     </div>
//                   </div>
//                   <div className="text-right">
//                     <div className="font-bold text-blue-600">
//                       ${flight.price || "N/A"}
//                     </div>
//                     <div className="text-xs text-gray-500">
//                       {flight.class || "Economy"}
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             ))}
//           {data.length > 3 && (
//             <button
//               className="text-xs text-blue-500 hover:text-blue-700 mt-2"
//               onClick={() => setIsExpanded(!isExpanded)}
//             >
//               {isExpanded ? "Show less" : `Show ${data.length - 3} more`}
//             </button>
//           )}
//         </div>
//       );
//     }

//     if (type === "hotels" && Array.isArray(data)) {
//       return (
//         <div className="space-y-2">
//           {data
//             .slice(0, isExpanded ? data.length : 3)
//             .map((hotel: any, index: number) => (
//               <div
//                 key={index}
//                 className="p-2 bg-gray-50 rounded border-l-4 border-green-400"
//               >
//                 <div className="flex justify-between items-start">
//                   <div>
//                     <div className="font-medium">{hotel.name || "Hotel"}</div>
//                     <div className="text-sm text-gray-600">
//                       {hotel.location || "Location"}
//                     </div>
//                     <div className="text-sm text-gray-500">
//                       {hotel.rating ? `${hotel.rating}★` : ""}{" "}
//                       {hotel.amenities ? `• ${hotel.amenities}` : ""}
//                     </div>
//                   </div>
//                   <div className="text-right">
//                     <div className="font-bold text-green-600">
//                       ${hotel.price || "N/A"}
//                     </div>
//                     <div className="text-xs text-gray-500">per night</div>
//                   </div>
//                 </div>
//               </div>
//             ))}
//           {data.length > 3 && (
//             <button
//               className="text-xs text-blue-500 hover:text-blue-700 mt-2"
//               onClick={() => setIsExpanded(!isExpanded)}
//             >
//               {isExpanded ? "Show less" : `Show ${data.length - 3} more`}
//             </button>
//           )}
//         </div>
//       );
//     }

//     if (type === "context") {
//       return (
//         <div className="text-sm text-gray-700">
//           {typeof data === "object" ? (
//             <pre className="whitespace-pre-wrap">
//               {JSON.stringify(data, null, 2)}
//             </pre>
//           ) : (
//             <p>{data}</p>
//           )}
//         </div>
//       );
//     }

//     return <div className="text-sm text-gray-500">No data available</div>;
//   };

//   return (
//     <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
//       <div className="flex items-center space-x-2 mb-2">
//         {icon}
//         <h3 className="text-sm font-medium text-gray-800">{title}</h3>
//       </div>
//       {renderContent()}
//     </div>
//   );
// };

// export default AIChat;

//(2)
"use client";
import {
  AlertCircle,
  Bot,
  Loader2,
  Mic,
  MicOff,
  Send,
  User,
} from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  status?: "sending" | "sent" | "error";
  results?: any;
  next_actions?: string[];
}

interface AIChatProps {
  conversationId?: string;
  className?: string;
}

const AIChat: React.FC<AIChatProps> = ({
  conversationId = "default",
  className = "",
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState("");

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const recognitionRef = useRef<any>(null);

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const getWebSocketUrl = (baseUrl: string) => {
    if (baseUrl.startsWith("https://")) {
      return baseUrl.replace("https://", "wss://");
    }
    return baseUrl.replace("http://", "ws://");
  };

  const WS_URL = `${getWebSocketUrl(API_BASE_URL)}/ws/${conversationId}`;

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        setSpeechSupported(true);
        recognitionRef.current = new SpeechRecognition();

        // Configure speech recognition
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = "en-US";

        // Handle speech recognition results
        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = "";
          let interimTranscript = "";

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript + " ";
            } else {
              interimTranscript += transcript;
            }
          }

          // Update transcript state for real-time display
          setTranscript(interimTranscript);

          // Update input field with final results
          if (finalTranscript) {
            setInput((prev) => prev + finalTranscript);
          }
        };

        // Handle speech recognition errors
        recognitionRef.current.onerror = (event: any) => {
          console.error("Speech recognition error:", event.error);
          setVoiceError(`Voice input error: ${event.error}`);
          setIsRecording(false);
          setTranscript("");
        };

        // Handle speech recognition end
        recognitionRef.current.onend = () => {
          setIsRecording(false);
          setTranscript("");
        };

        // Handle speech recognition start
        recognitionRef.current.onstart = () => {
          setVoiceError(null);
          setTranscript("");
        };
      } else {
        setSpeechSupported(false);
        setVoiceError(
          "Speech recognition not supported in this browser. Try Chrome, Edge, or Safari."
        );
      }
    }
  }, []);

  useEffect(() => {
    initializeWebSocket();

    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content:
          "🌟 Welcome to the GKE Turns 10 hackathon demo! I'm your AI travel assistant powered by multi-agent architecture. I can help you search for flights, find hotels, and plan amazing trips. You can type or use voice input! What travel adventure can I help you with today?",
        timestamp: new Date().toISOString(),
      },
    ]);

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (recognitionRef.current && isRecording) {
        recognitionRef.current.stop();
      }
    };
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeWebSocket = () => {
    try {
      if (connectionAttempts < 3) {
        wsRef.current = new WebSocket(WS_URL);
        setConnectionAttempts((prev) => prev + 1);

        wsRef.current.onopen = () => {
          setIsConnected(true);
          setConnectionAttempts(0);
          console.log("WebSocket connected");
        };

        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === "chat_response") {
            handleWebSocketMessage(data.data);
          }
        };

        wsRef.current.onclose = () => {
          setIsConnected(false);
          console.log("WebSocket disconnected");

          if (reconnectTimeout.current) {
            clearTimeout(reconnectTimeout.current);
          }

          if (connectionAttempts < 3) {
            reconnectTimeout.current = setTimeout(() => {
              if (
                !wsRef.current ||
                wsRef.current.readyState === WebSocket.CLOSED
              ) {
                initializeWebSocket();
              }
            }, 5000);
          }
        };

        wsRef.current.onerror = (error) => {
          console.error("WebSocket error:", error);
          setIsConnected(false);
        };
      } else {
        setIsConnected(false);
        console.log(
          "WebSocket connection failed after 3 attempts. Running in demo mode."
        );
      }
    } catch (error) {
      console.error("Failed to initialize WebSocket:", error);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    console.log("WebSocket message:", data);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Real voice recording functionality
  const toggleRecording = async () => {
    if (!speechSupported) {
      setVoiceError("Speech recognition not supported in this browser");
      return;
    }

    if (!isRecording) {
      try {
        // Request microphone permission
        await navigator.mediaDevices.getUserMedia({ audio: true });

        setIsRecording(true);
        setVoiceError(null);
        recognitionRef.current.start();
      } catch (error) {
        setVoiceError(
          "Microphone access denied. Please allow microphone permissions."
        );
        console.error("Microphone access error:", error);
      }
    } else {
      setIsRecording(false);
      setTranscript("");
      recognitionRef.current.stop();
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
      status: "sending",
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentInput,
          conversation_id: conversationId,
          user_context: {},
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id ? { ...msg, status: "sent" } : msg
        )
      );

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.message,
        timestamp: data.timestamp
          ? new Date(data.timestamp).toISOString()
          : new Date().toISOString(),
        results: data.results,
        next_actions: data.next_actions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id ? { ...msg, status: "error" } : msg
        )
      );

      // Enhanced demo response
      const demoResponse: Message = {
        id: `demo-${Date.now()}`,
        role: "assistant",
        content: `🎯 **AI Travel Assistant Response**\n\n"${currentInput}"\n\n✈️ **Simulated Search Results:**\n• Paris flights: $650-$890 (Dec 15-22)\n• Hotel options: 4-star from $120/night\n• Weather: Winter, 5°C, pack warm clothes\n• Attractions: Eiffel Tower, Louvre Museum\n\n📱 **Voice Input Working:** ${currentInput.toLowerCase().includes("voice") || currentInput.toLowerCase().includes("speak") ? "Yes! I heard you clearly through voice input! 🎙️" : "Try using the microphone button for voice input!"}\n\n*Demo mode - Backend at localhost:8000 not running*`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, demoResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === "user";

    return (
      <div
        key={message.id}
        className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
      >
        <div
          className={`flex max-w-3xl ${isUser ? "flex-row-reverse" : "flex-row"}`}
        >
          <div className={`flex-shrink-0 ${isUser ? "ml-3" : "mr-3"}`}>
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                isUser
                  ? "bg-gradient-to-r from-blue-500 to-blue-600"
                  : "bg-gradient-to-r from-teal-500 to-green-500"
              }`}
            >
              {isUser ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-white" />
              )}
            </div>
          </div>

          <div className={`flex-1 ${isUser ? "text-right" : "text-left"}`}>
            <div
              className={`inline-block p-3 rounded-lg max-w-md ${
                isUser
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-gray-100 text-gray-800 rounded-bl-none border border-gray-200"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </p>

              {message.status === "sending" && (
                <div className="flex items-center justify-end mt-2">
                  <Loader2 className="w-3 h-3 animate-spin mr-1" />
                  <span className="text-xs opacity-75">Sending...</span>
                </div>
              )}

              {message.status === "error" && (
                <div className="text-red-300 text-xs mt-1">Failed to send</div>
              )}
            </div>

            {message.next_actions && message.next_actions.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {message.next_actions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(action)}
                    className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full hover:bg-blue-200 transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            )}

            <div className="text-xs text-gray-400 mt-1">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-teal-500 to-blue-600">
        <div>
          <h2 className="text-lg font-semibold text-white">
            AI Travel Assistant
          </h2>
          <p className="text-sm text-teal-100">
            Hackathon Demo - Multi-Agent Architecture
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-green-400" : "bg-red-400"
            }`}
          ></div>
          <span className="text-xs text-teal-100">
            {isConnected
              ? "Connected"
              : connectionAttempts >= 3
                ? "Demo Mode"
                : "Connecting..."}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map(renderMessage)}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2 p-3 bg-white rounded-lg shadow-sm border">
              <Loader2 className="w-4 h-4 animate-spin text-teal-500" />
              <span className="text-sm text-gray-600">AI is thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Voice Error Display */}
      {voiceError && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-xs text-red-600">{voiceError}</span>
            <button
              onClick={() => setVoiceError(null)}
              className="text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Input Section */}
      <div className="p-4 border-t bg-white">
        <div className="flex items-end space-x-2">
          {/* Voice Input Button */}
          <button
            onClick={toggleRecording}
            disabled={!speechSupported}
            title={
              !speechSupported
                ? "Voice input not supported in this browser"
                : isRecording
                  ? "Stop Recording"
                  : "Start Voice Input"
            }
            className={`flex-shrink-0 p-3 rounded-lg border-2 transition-all duration-200 mb-3 ${
              !speechSupported
                ? "bg-gray-200 border-gray-300 text-gray-400 cursor-not-allowed"
                : isRecording
                  ? "bg-red-500 border-red-500 text-white animate-pulse"
                  : "bg-white border-teal-500 text-teal-500 hover:bg-teal-50"
            }`}
          >
            {isRecording ? (
              <MicOff className="w-4 h-4" />
            ) : (
              <Mic className="w-4 h-4" />
            )}
          </button>

          {/* Text Input */}
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                speechSupported
                  ? "Type or use voice input for flights, hotels, travel planning..."
                  : "Ask me about flights, hotels, or travel planning..."
              }
              className="w-full text-black p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              rows={1}
              disabled={isLoading}
            />
          </div>

          {/* Send Button */}
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 mb-3 p-3 bg-gradient-to-r from-teal-500 to-blue-600 text-white rounded-lg hover:from-teal-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* Recording Indicator */}
        {isRecording && (
          <div className="mt-2 flex items-center justify-center">
            <div className="flex items-center space-x-2 px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span>🎙️ Listening... Speak now</span>
              {transcript && (
                <span className="ml-2 text-gray-600">"{transcript}"</span>
              )}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mt-3">
          {[
            "Search flights to Paris",
            "Find hotels in London",
            "Plan a romantic getaway",
            "Budget trip to Japan",
            "Test voice input",
          ].map((suggestion, index) => (
            <button
              key={index}
              onClick={() => setInput(suggestion)}
              className="text-xs px-3 py-1 bg-teal-100 text-teal-700 rounded-full hover:bg-teal-200 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>

        {/* Voice Support Status */}
        <div className="mt-2 flex items-center justify-center">
          <span
            className={`text-xs ${speechSupported ? "text-green-600" : "text-red-600"}`}
          >
            🎤 Voice Input:{" "}
            {speechSupported ? "Available" : "Not supported in this browser"}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AIChat;
