const TOKENS_KEY = 'cognito_tokens';

export const tokenStorage = {
  get: () => {
    if (typeof window === 'undefined') return null;
    try {
      const tokens = sessionStorage.getItem(TOKENS_KEY);
      return tokens ? JSON.parse(tokens) : null;
    } catch {
      return null;
    }
  },

  set: (tokens: any) => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
    }
  },

  clear: () => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(TOKENS_KEY);
    }
  },

  isAuthenticated: () => {
    const tokens = tokenStorage.get();
    return tokens && tokens.AccessToken;
  },
};
