interface TokenData {
  AccessToken: string;
  IdToken: string;
  RefreshToken: string;
}

export const getStoredTokens = (): TokenData | null => {
  if (typeof window === "undefined") return null;

  try {
    const tokens = localStorage.getItem("cognito_tokens");
    return tokens ? (JSON.parse(tokens) as TokenData) : null;
  } catch {
    return null;
  }
};

export const isAuthenticated = (): boolean => {
  const tokens = getStoredTokens();
  return Boolean(tokens?.AccessToken);
};

export const clearTokens = (): void => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("cognito_tokens");
  }
};
