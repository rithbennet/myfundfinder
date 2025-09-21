export const getStoredTokens = () => {
  if (typeof window === 'undefined') return null;
  
  try {
    const tokens = localStorage.getItem('cognito_tokens');
    return tokens ? JSON.parse(tokens) : null;
  } catch {
    return null;
  }
};

export const isAuthenticated = () => {
  const tokens = getStoredTokens();
  return tokens && tokens.AccessToken;
};

export const clearTokens = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('cognito_tokens');
  }
};
