interface TokenData {
  AccessToken: string;
  IdToken: string;
  RefreshToken: string;
}

const getCookie = (name: string): string | null => {
  if (typeof document === "undefined") return null;
  
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
};

export const getStoredTokens = (): TokenData | null => {
  if (typeof window === "undefined") return null;

  try {
    // Check cookies first
    const authToken = getCookie("auth-token");
    if (authToken) {
      return {
        AccessToken: authToken,
        IdToken: getCookie("id-token") || "",
        RefreshToken: getCookie("refresh-token") || "",
      };
    }

    // Fallback to localStorage
    const tokens = localStorage.getItem("cognito_tokens");
    if (tokens) {
      return JSON.parse(tokens) as TokenData;
    }

    const accessToken = localStorage.getItem("accessToken");
    if (accessToken) {
      return {
        AccessToken: accessToken,
        IdToken: localStorage.getItem("idToken") || "",
        RefreshToken: localStorage.getItem("refreshToken") || "",
      };
    }

    return null;
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
    localStorage.removeItem("accessToken");
    localStorage.removeItem("idToken");
    localStorage.removeItem("refreshToken");
  }
};
