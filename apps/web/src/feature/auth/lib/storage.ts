interface TokenData {
  AccessToken: string;
  IdToken: string;
  RefreshToken: string;
}

const TOKENS_KEY = "cognito_tokens";

export const tokenStorage = {
  get: (): TokenData | null => {
    if (typeof window === "undefined") return null;
    try {
      const tokens = sessionStorage.getItem(TOKENS_KEY);
      return tokens ? (JSON.parse(tokens) as TokenData) : null;
    } catch {
      return null;
    }
  },

  set: (tokens: TokenData): void => {
    if (typeof window !== "undefined") {
      sessionStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
    }
  },

  clear: (): void => {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(TOKENS_KEY);
    }
  },

  isAuthenticated: (): boolean => {
    const tokens = tokenStorage.get();
    return Boolean(tokens?.AccessToken);
  },
};
