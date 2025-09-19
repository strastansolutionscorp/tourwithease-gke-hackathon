import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    COGNITO_LOCAL_URL: "http://localhost:3000",
    COGNITO_PROD_URL: "https://dev.d3nsakwmjtwece.amplifyapp.com",
    COGNITO_CLIENT_ID: "3j99l5kkd0g4dije4dg8r9enn7",
    COGNITO_DOMAIN:
      "https://ap-southeast-1ybwkprqn4.auth.ap-southeast-1.amazoncognito.com",
    COGNITO_AUTHORITY:
      "https://cognito-idp.ap-southeast-1.amazonaws.com/ap-southeast-1_YBwkpRQN4",
    ENV: "Dev", // Use Dev for localhost
    NEXT_PUBLIC_API_URL:
      "https://dsp9w2xzm5.execute-api.ap-southeast-1.amazonaws.com/prod",
    NEXT_PUBLIC_API_BASE_URL:
      "https://9u7ako2yz0.execute-api.ap-southeast-1.amazonaws.com/prod",
  },
  reactStrictMode: true,
  swcMinify: true,
};

export default nextConfig;
