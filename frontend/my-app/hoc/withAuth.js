"use client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "react-oidc-context";

export function withAuth(Component) {
  return function ProtectedComponent(props) {
    const auth = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!auth.isLoading && !auth.isAuthenticated) {
        router.push("/"); // Redirect unauthenticated users
      }
    }, [auth, router]);

    if (auth.isLoading) {
      return <div>Loading...</div>;
    }

    return <Component {...props} />;
  };
}
