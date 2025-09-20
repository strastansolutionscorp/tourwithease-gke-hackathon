// "use client";
// import { AuthProvider } from "react-oidc-context";
// import { oidcConfigSignInConfig } from "../src/utils/oidcConfigSignInConfig";

// export default function AuthWrapper({ children }) {
//   return <AuthProvider {...oidcConfigSignInConfig}>{children}</AuthProvider>;
// }

//(2)
// "use client";
// import { AuthProvider } from "react-oidc-context";
// import { oidcConfigSignInConfig } from "../src/utils/oidcConfigSigninConfig.js";

// export default function AuthWrapper({ children }: { children: any }) {
//   return <AuthProvider {...oidcConfigSignInConfig}>{children}</AuthProvider>;
// }

//(3)
"use client";
import { AuthProvider } from "react-oidc-context";
import { oidcConfigSignInConfig } from "../src/utils/oidcConfigSigninConfig.js";

export default function AuthWrapper({ children }: { children: any }) {
  const config = {
    ...oidcConfigSignInConfig,
    authority: oidcConfigSignInConfig.authority!,
    client_id: oidcConfigSignInConfig.client_id!,
  };

  return <AuthProvider {...config}>{children}</AuthProvider>;
}
