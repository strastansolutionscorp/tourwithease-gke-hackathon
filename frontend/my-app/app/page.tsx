//(1)
// "use client";

// import AIChat from "@/components/AIChat";
// import { Globe, MessageCircle } from "lucide-react";

// export default function GKETurns10Demo() {
//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex flex-col">
//       {/* Header */}
//       <header className="bg-white shadow-sm border-b border-gray-200">
//         <div className="max-w-6xl mx-auto px-4 py-4">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center space-x-4">
//               <div className="relative">
//                 <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center">
//                   <div className="relative">
//                     <Globe className="w-8 h-8 text-white" />
//                     <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-sm flex items-center justify-center">
//                       <MessageCircle className="w-3 h-3 text-white" />
//                     </div>
//                   </div>
//                 </div>
//               </div>
//               <div>
//                 <h1 className="text-2xl font-bold text-gray-900">
//                   Agentic Travel
//                 </h1>
//                 <p className="text-sm text-teal-600 font-medium">
//                   AI SOLUTIONS
//                 </p>
//                 <p className="text-xs text-gray-500">GKE Turns 10 - POC Demo</p>
//               </div>
//             </div>
//             {/* Voice button removed from here - now in chat input */}
//           </div>
//         </div>
//       </header>

//       {/* Main Content */}
//       <div className="flex-1 max-w-6xl mx-auto w-full px-4 py-6 flex flex-col">
//         <div className="flex-1 bg-white rounded-lg shadow-lg border border-gray-200 flex flex-col overflow-hidden">
//           <div className="h-[75vh]">
//             <AIChat conversationId="gke-demo-chat" className="h-full" />
//           </div>
//         </div>

//         {/* Demo Info Footer */}
//         <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
//           <div className="p-4 bg-blue-50 rounded-lg">
//             <h3 className="text-sm font-medium text-blue-800 mb-2">
//               🚀 GKE Turns 10 Hackathon 2024
//             </h3>
//             <p className="text-sm text-blue-600 mb-3">
//               Multi-agent AI architecture with ADK + A2A protocol on Google
//               Kubernetes Engine
//             </p>
//             <div className="text-xs text-blue-600 space-y-1">
//               <div>✅ Real-time WebSocket chat</div>
//               <div>✅ Flight & hotel search integration</div>
//               <div>🔄 TWE backend environment</div>
//             </div>
//           </div>

//           <div className="p-4 bg-green-50 rounded-lg">
//             <h3 className="text-sm font-medium text-green-800 mb-2">
//               💡 Try These Examples:
//             </h3>
//             <div className="text-xs text-green-600 space-y-1">
//               <div>"Plan a romantic trip to Paris next week"</div>
//               <div>"Find flights from NYC to London"</div>
//               <div>"Recommend hotels in Tokyo under $200/night"</div>
//             </div>
//           </div>
//         </div>

//         <div className="mt-4 text-center text-xs text-gray-500">
//           <p>Agentic Travel AI Solutions • Backend: TWE Test Environment</p>
//         </div>
//       </div>
//     </div>
//   );
// }

//(2 with mfa)
// "use client";

// import AIChat from "@/components/AIChat";
// import AuthWrapper from "@/components/AuthWrapper";
// import { Globe, Loader2, LogOut, MessageCircle } from "lucide-react";
// import { useEffect } from "react";
// import { useAuth } from "react-oidc-context";

// // Separate the main content into a new component
// function MainContent({ auth }: { auth: any }) {
//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex flex-col">
//       {/* Header */}
//       <header className="bg-white shadow-sm border-b border-gray-200">
//         <div className="max-w-6xl mx-auto px-4 py-4">
//           <div className="flex items-center justify-between">
//             <div className="flex items-center space-x-4">
//               <div className="relative">
//                 <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center">
//                   <div className="relative">
//                     <Globe className="w-8 h-8 text-white" />
//                     <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-sm flex items-center justify-center">
//                       <MessageCircle className="w-3 h-3 text-white" />
//                     </div>
//                   </div>
//                 </div>
//               </div>
//               <div>
//                 <h1 className="text-2xl font-bold text-gray-900">
//                   Agentic Travel
//                 </h1>
//                 <p className="text-sm text-teal-600 font-medium">
//                   AI SOLUTIONS
//                 </p>
//                 <p className="text-xs text-gray-500">GKE Turns 10 - POC Demo</p>
//               </div>
//             </div>

//             {/* Add User Profile & Logout */}
//             <div className="flex items-center space-x-4">
//               <div className="text-right">
//                 <p className="text-sm font-medium text-gray-900">
//                   {auth.user?.profile.name || auth.user?.profile.email}
//                 </p>
//                 <p className="text-xs text-gray-500">
//                   {auth.user?.profile.email}
//                 </p>
//               </div>
//               <button
//                 onClick={() => auth.removeUser()}
//                 className="p-2 text-gray-600 hover:text-red-600 transition-colors"
//                 title="Sign Out"
//               >
//                 <LogOut className="w-5 h-5" />
//               </button>
//             </div>
//           </div>
//         </div>
//       </header>

//       {/* Main Content */}
//       <div className="flex-1 max-w-6xl mx-auto w-full px-4 py-6 flex flex-col">
//         <div className="flex-1 bg-white rounded-lg shadow-lg border border-gray-200 flex flex-col overflow-hidden">
//           <div className="h-[75vh]">
//             <AIChat conversationId="gke-demo-chat" className="h-full" />
//           </div>
//         </div>

//         {/* Demo Info Footer */}
//         <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
//           <div className="p-4 bg-blue-50 rounded-lg">
//             <h3 className="text-sm font-medium text-blue-800 mb-2">
//               🚀 GKE Turns 10 Hackathon 2024
//             </h3>
//             <p className="text-sm text-blue-600 mb-3">
//               Multi-agent AI architecture with ADK + A2A protocol on Google
//               Kubernetes Engine
//             </p>
//             <div className="text-xs text-blue-600 space-y-1">
//               <div>✅ Real-time WebSocket chat</div>
//               <div>✅ Flight & hotel search integration</div>
//               <div>🔄 TWE backend environment</div>
//             </div>
//           </div>

//           <div className="p-4 bg-green-50 rounded-lg">
//             <h3 className="text-sm font-medium text-green-800 mb-2">
//               💡 Try These Examples:
//             </h3>
//             <div className="text-xs text-green-600 space-y-1">
//               <div>"Plan a romantic trip to Paris next week"</div>
//               <div>"Find flights from NYC to London"</div>
//               <div>"Recommend hotels in Tokyo under $200/night"</div>
//             </div>
//           </div>
//         </div>

//         <div className="mt-4 text-center text-xs text-gray-500">
//           <p>Agentic Travel AI Solutions • Backend: TWE Test Environment</p>
//         </div>
//       </div>
//     </div>
//   );
// }

// // Loading component
// function LoadingState() {
//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
//       <div className="text-center">
//         <Loader2 className="w-8 h-8 animate-spin text-teal-500 mx-auto mb-4" />
//         <p className="text-gray-600">Loading your travel experience...</p>
//       </div>
//     </div>
//   );
// }

// // Error component
// function ErrorState({ message }: { message: string }) {
//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
//       <div className="max-w-md p-8 bg-white rounded-lg shadow-lg">
//         <h2 className="text-xl font-bold text-red-600 mb-4">
//           Authentication Error
//         </h2>
//         <p className="text-gray-600 mb-4">{message}</p>
//         <button
//           onClick={() => window.location.reload()}
//           className="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition-colors"
//         >
//           Try Again
//         </button>
//       </div>
//     </div>
//   );
// }

// // Main component with auth wrapper
// export default function GKETurns10Demo() {
//   return (
//     <AuthWrapper>
//       <AuthContent />
//     </AuthWrapper>
//   );
// }

// // Auth content component
// function AuthContent() {
//   const auth = useAuth();

//   useEffect(() => {
//     if (!auth.isLoading && !auth.isAuthenticated) {
//       auth.signinRedirect();
//     }
//   }, [auth]);

//   if (auth.isLoading) {
//     return <LoadingState />;
//   }

//   if (auth.error) {
//     return <ErrorState message={auth.error.message} />;
//   }

//   if (!auth.isAuthenticated) {
//     return (
//       <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
//         <div className="text-center">
//           <Loader2 className="w-8 h-8 animate-spin text-teal-500 mx-auto mb-4" />
//           <p className="text-gray-600">Redirecting to sign in...</p>
//         </div>
//       </div>
//     );
//   }

//   return <MainContent auth={auth} />;
// }

//(3)
"use client";

import AIChat from "@/components/AIChat";
import AuthWrapper from "@/components/AuthWrapper";
import oidcConfigSignOutConfig from "@/src/utils/oidcConfigSignOutConfig";
import { Loader2, LogOut } from "lucide-react";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";

// Sign In Page Component
function SignInPage({ onSignIn }: { onSignIn: () => void }) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = () => {
    setIsLoading(true);
    onSignIn();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Logo/Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center mx-auto mb-4">
              {/* <div className="relative">
                <Globe className="w-10 h-10 text-white" />
                <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-sm flex items-center justify-center">
                  <MessageCircle className="w-3 h-3 text-white" />
                </div>
              </div> */}
              <Image
                src="/images/agentic-travel-image.png"
                alt="Agentic Travel Logo"
                width={80}
                height={80}
                className="w-full h-full object-contain"
              />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Agentic Travel
            </h1>
            <p className="text-sm text-teal-600 font-medium">AI SOLUTIONS</p>
            <p className="text-xs text-gray-500">GKE Turns 10 - POC Demo</p>
          </div>

          {/* Sign In Content */}
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Welcome Back
              </h2>
              <p className="text-gray-600 text-sm">
                Sign in to continue your AI-powered travel experience
              </p>
            </div>

            {/* Sign In with Google Button */}
            <button
              onClick={handleSignIn}
              disabled={isLoading}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
              ) : (
                <>
                  {/* Google Icon */}
                  <svg
                    className="w-5 h-5 mr-3"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      fill="#EA4335"
                    />
                  </svg>
                  <span className="text-gray-700 font-medium">
                    Sign in with Google
                  </span>
                </>
              )}
            </button>

            {/* Demo Info */}
            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-medium text-blue-800 mb-2">
                🚀 GKE Turns 10 Hackathon 2024
              </h3>
              <p className="text-xs text-blue-600 mb-2">
                Multi-agent AI architecture with ADK + A2A protocol on Google
                Kubernetes Engine
              </p>
              <div className="text-xs text-blue-600 space-y-1">
                <div>✅ Real-time WebSocket chat</div>
                <div>✅ Flight & hotel search integration</div>
                <div>🔄 TWE backend environment</div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Agentic Travel AI Solutions • Backend: TWE Test Environment</p>
        </div>
      </div>
    </div>
  );
}

// Separate the main content into a new component
function MainContent({ auth }: { auth: any }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                {/* <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center">
                  <div className="relative">
                    <Globe className="w-8 h-8 text-white" />
                    <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-sm flex items-center justify-center">
                      <MessageCircle className="w-3 h-3 text-white" />
                    </div>
                  </div>
                </div> */}
                <div className="w-20 h-20">
                  <Image
                    src="/images/agentic-travel-image.png"
                    alt="Agentic Travel Logo"
                    width={64}
                    height={64}
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Agentic Travel
                </h1>
                <p className="text-sm text-teal-600 font-medium">
                  AI SOLUTIONS
                </p>
                <p className="text-xs text-gray-500">GKE Turns 10 - POC Demo</p>
              </div>
            </div>

            {/* Add User Profile & Logout */}
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {auth.user?.profile.name || auth.user?.profile.email}
                </p>
                <p className="text-xs text-gray-500">
                  {auth.user?.profile.email}
                </p>
              </div>
              <button
                onClick={() => oidcConfigSignOutConfig()}
                className="p-2 text-gray-600 hover:text-red-600 transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      {/* Main Content - Side by Side Layout */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <div className="flex gap-4 h-[calc(100vh-12rem)]">
          {/* Chat Box - Left Side */}
          <div className="flex-1 bg-white rounded-lg shadow-lg border border-gray-200 flex flex-col overflow-hidden">
            <AIChat conversationId="gke-demo-chat" className="h-full" />
          </div>

          {/* Info Panels - Right Side */}
          <div className="w-96 flex flex-col gap-4">
            {/* GKE Hackathon Info - Interactive */}
            <div className="group p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-md cursor-pointer">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-blue-800 group-hover:text-blue-900 transition-colors">
                  🚀 GKE Turns 10 Hackathon 2024
                </h3>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              </div>
              <p className="text-sm text-blue-700 mb-3 group-hover:text-blue-800 transition-colors">
                Multi-agent AI architecture with ADK + A2A protocol on Google
                Kubernetes Engine
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-xs text-blue-600 group-hover:text-blue-700 transition-all duration-200 hover:translate-x-1">
                  <div className="w-4 h-4 flex items-center justify-center mr-2">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                  Real-time WebSocket chat
                </div>
                <div className="flex items-center text-xs text-blue-600 group-hover:text-blue-700 transition-all duration-200 hover:translate-x-1">
                  <div className="w-4 h-4 flex items-center justify-center mr-2">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                  Flight & hotel search integration
                </div>
                <div className="flex items-center text-xs text-blue-600 group-hover:text-blue-700 transition-all duration-200 hover:translate-x-1">
                  <div className="w-4 h-4 flex items-center justify-center mr-2">
                    <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full animate-pulse"></div>
                  </div>
                  TWE backend environment
                </div>
              </div>
              <div className="mt-3 text-xs text-blue-500 group-hover:text-blue-600 transition-colors">
                Click to learn more about our architecture
              </div>
            </div>

            {/* Try Examples - Interactive */}
            <div className="flex-1 p-4 bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg border border-green-200 hover:border-green-300 transition-all duration-300 hover:shadow-md">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-green-800">
                  💡 Try These Examples:
                </h3>
                <div className="text-xs text-green-600 animate-pulse">
                  Click to try!
                </div>
              </div>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    const event = new CustomEvent("sendMessage", {
                      detail: {
                        message: "Plan a romantic trip to Paris next week",
                      },
                    });
                    window.dispatchEvent(event);
                  }}
                  className="w-full text-left p-2 text-xs text-green-700 bg-white/50 rounded border border-green-200 hover:border-green-400 hover:bg-white hover:shadow-sm transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] group"
                >
                  <div className="flex items-center">
                    <span className="text-green-500 mr-2 group-hover:animate-bounce">
                      ✈️
                    </span>
                    <span className="group-hover:font-medium">
                      "Plan a romantic trip to Paris next week"
                    </span>
                  </div>
                </button>

                <button
                  onClick={() => {
                    const event = new CustomEvent("sendMessage", {
                      detail: { message: "Find flights from NYC to London" },
                    });
                    window.dispatchEvent(event);
                  }}
                  className="w-full text-left p-2 text-xs text-green-700 bg-white/50 rounded border border-green-200 hover:border-green-400 hover:bg-white hover:shadow-sm transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] group"
                >
                  <div className="flex items-center">
                    <span className="text-green-500 mr-2 group-hover:animate-bounce">
                      🛫
                    </span>
                    <span className="group-hover:font-medium">
                      "Find flights from NYC to London"
                    </span>
                  </div>
                </button>

                <button
                  onClick={() => {
                    const event = new CustomEvent("sendMessage", {
                      detail: {
                        message: "Recommend hotels in Tokyo under $200/night",
                      },
                    });
                    window.dispatchEvent(event);
                  }}
                  className="w-full text-left p-2 text-xs text-green-700 bg-white/50 rounded border border-green-200 hover:border-green-400 hover:bg-white hover:shadow-sm transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] group"
                >
                  <div className="flex items-center">
                    <span className="text-green-500 mr-2 group-hover:animate-bounce">
                      🏨
                    </span>
                    <span className="group-hover:font-medium">
                      "Recommend hotels in Tokyo under $200/night"
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-4 text-center text-xs text-gray-500">
          <p>Agentic Travel AI Solutions • Backend: TWE Test Environment</p>
        </div>
      </div>
    </div>
  );
}

// Loading component
function LoadingState() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-500 mx-auto mb-4" />
        <p className="text-gray-600">Loading your travel experience...</p>
      </div>
    </div>
  );
}

// Error component
function ErrorState({ message }: { message: string }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
      <div className="max-w-md p-8 bg-white rounded-lg shadow-lg">
        <h2 className="text-xl font-bold text-red-600 mb-4">
          Authentication Error
        </h2>
        <p className="text-gray-600 mb-4">{message}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

// Main component with auth wrapper
export default function GKETurns10Demo() {
  return (
    <AuthWrapper>
      <AuthContent />
    </AuthWrapper>
  );
}

// Auth content component
function AuthContent() {
  const auth = useAuth();
  const [showSignInPage, setShowSignInPage] = useState(true);

  // Remove the automatic redirect effect
  useEffect(() => {
    // Only check authentication status, don't auto-redirect
    if (auth.isAuthenticated) {
      setShowSignInPage(false);
    }
  }, [auth.isAuthenticated]);

  const handleSignIn = () => {
    setShowSignInPage(false);
    auth.signinRedirect();
  };

  if (auth.isLoading) {
    return <LoadingState />;
  }

  if (auth.error) {
    return <ErrorState message={auth.error.message} />;
  }

  // Show sign in page if not authenticated and user hasn't clicked sign in
  if (!auth.isAuthenticated && showSignInPage) {
    return <SignInPage onSignIn={handleSignIn} />;
  }

  // Show loading while redirecting or processing authentication
  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-teal-500 mx-auto mb-4" />
          <p className="text-gray-600">Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  return <MainContent auth={auth} />;
}
