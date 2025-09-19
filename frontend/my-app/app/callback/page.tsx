// "use client";

// import { useRouter } from "next/navigation";
// import { useEffect, useState } from "react";
// import { RotatingLines } from "react-loader-spinner";
// import { useAuth } from "react-oidc-context";

// export default function AuthCallback() {
//   const auth = useAuth();
//   const router = useRouter();
//   const [error, setError] = useState<string | null>(null);

//   useEffect(() => {
//     let timeoutId: NodeJS.Timeout;

//     const handleAuth = async () => {
//       if (!auth.isLoading) {
//         if (auth.isAuthenticated && auth.user) {
//           try {
//             const userData = auth.user;
//             const userProfile = auth.user.profile;
//             console.log("Auth successful:", { userProfile, userData });

//             timeoutId = setTimeout(() => {
//               router.push("/");
//             }, 1000);
//           } catch (err) {
//             console.error("Error processing authentication:", err);
//             setError("Failed to process authentication. Please try again.");
//           }
//         } else if (auth.error) {
//           console.error("Authentication error:", auth.error.message);
//           setError(auth.error.message || "Authentication failed");
//         }
//       }
//     };

//     handleAuth();

//     return () => {
//       if (timeoutId) clearTimeout(timeoutId);
//     };
//   }, [auth, router]);

//   if (error) {
//     return (
//       <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
//         <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
//           <div className="text-red-600 text-center mb-4">
//             <svg
//               className="w-12 h-12 mx-auto mb-4"
//               fill="none"
//               stroke="currentColor"
//               viewBox="0 0 24 24"
//             >
//               <path
//                 strokeLinecap="round"
//                 strokeLinejoin="round"
//                 strokeWidth={2}
//                 d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
//               />
//             </svg>
//             <h3 className="text-lg font-semibold">Authentication Error</h3>
//             <p className="text-sm text-gray-600 mt-2">{error}</p>
//           </div>
//           <button
//             onClick={() => auth.signinRedirect()}
//             className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
//           >
//             Try Again
//           </button>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
//       <div className="text-center">
//         <RotatingLines
//           strokeColor="#0070f3"
//           strokeWidth="5"
//           animationDuration="0.75"
//           width="96"
//           visible={true}
//         />
//         <div className="mt-8 space-y-2">
//           <h2 className="text-xl font-semibold text-gray-900">
//             Processing Your Login
//           </h2>
//           <p className="text-sm text-gray-600">
//             Please wait while we authenticate your session...
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// }

//(2)
"use client";

import { Globe, Loader2, MessageCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";

export default function AuthCallback() {
  const auth = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleAuth = async () => {
      if (!auth.isLoading) {
        if (auth.isAuthenticated && auth.user) {
          try {
            const userData = auth.user;
            const userProfile = auth.user.profile;
            console.log("Auth successful:", { userProfile, userData });

            timeoutId = setTimeout(() => {
              router.push("/");
            }, 1000);
          } catch (err) {
            console.error("Error processing authentication:", err);
            setError("Failed to process authentication. Please try again.");
          }
        } else if (auth.error) {
          console.error("Authentication error:", auth.error.message);
          setError(auth.error.message || "Authentication failed");
        }
      }
    };

    handleAuth();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [auth, router]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-lg shadow-xl p-8">
            {/* Logo/Header */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center mx-auto mb-4">
                <div className="relative">
                  <Globe className="w-10 h-10 text-white" />
                  <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-sm flex items-center justify-center">
                    <MessageCircle className="w-3 h-3 text-white" />
                  </div>
                </div>
              </div>
              <h1 className="text-xl font-bold text-gray-900 mb-1">
                Agentic Travel
              </h1>
              <p className="text-sm text-teal-600 font-medium">AI SOLUTIONS</p>
            </div>

            {/* Error Content */}
            <div className="text-center space-y-4">
              <div className="text-red-600">
                <svg
                  className="w-12 h-12 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <h3 className="text-lg font-semibold text-gray-900">
                  Authentication Error
                </h3>
                <p className="text-sm text-gray-600 mt-2">{error}</p>
              </div>

              <button
                onClick={() => auth.signinRedirect()}
                className="w-full bg-teal-600 text-white py-3 px-4 rounded-lg hover:bg-teal-700 transition-colors font-medium"
              >
                Try Again
              </button>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-6 text-center text-xs text-gray-500">
            <p>Agentic Travel AI Solutions • GKE Turns 10 - POC Demo</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center p-4">
      <div className="text-center">
        {/* Logo */}
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-teal-400 to-blue-600 flex items-center justify-center mx-auto mb-6">
          <div className="relative">
            <Globe className="w-10 h-10 text-white" />
            <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-green-500 rounded-sm flex items-center justify-center">
              <MessageCircle className="w-3 h-3 text-white" />
            </div>
          </div>
        </div>

        {/* Loading Spinner - Properly Centered */}
        <div className="flex justify-center items-center mb-6">
          <Loader2 className="w-12 h-12 animate-spin text-teal-500" />
        </div>

        {/* Loading Text */}
        <div className="space-y-2 max-w-sm mx-auto">
          <h2 className="text-xl font-semibold text-gray-900">
            Processing Your Login
          </h2>
          <p className="text-sm text-gray-600">
            Please wait while we authenticate your session...
          </p>
        </div>

        {/* App Info */}
        <div className="mt-8 text-center">
          <h3 className="text-lg font-bold text-gray-800 mb-1">
            Agentic Travel
          </h3>
          <p className="text-sm text-teal-600 font-medium">AI SOLUTIONS</p>
          <p className="text-xs text-gray-500 mt-1">GKE Turns 10 - POC Demo</p>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-gray-500">
          <p>Agentic Travel AI Solutions • Backend: TWE Test Environment</p>
        </div>
      </div>
    </div>
  );
}
