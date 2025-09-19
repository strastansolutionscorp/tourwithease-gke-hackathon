"use client";
import { oidcConfigSignInConfig } from "@/src/utils/oidcConfigSignInConfig";
import { AuthProvider } from "react-oidc-context";

export default function AuthWrapper({ children }) {
  return <AuthProvider {...oidcConfigSignInConfig}>{children}</AuthProvider>;
}
