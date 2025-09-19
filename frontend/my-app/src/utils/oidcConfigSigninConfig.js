const uri =
  process.env.ENV == "Dev"
    ? process.env.COGNITO_LOCAL_URL
    : process.env.COGNITO_PROD_URL;

export const oidcConfigSignInConfig = {
  authority: process.env.COGNITO_AUTHORITY,
  client_id: process.env.COGNITO_CLIENT_ID,
  redirect_uri: `${uri}/callback`,
  response_type: "code",
  scope: "email openid phone profile",
};
