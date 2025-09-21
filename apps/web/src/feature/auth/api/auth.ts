// Types for auth API responses
interface AuthSuccessResponse {
  success: true;
  message?: string;
  user?: {
    id: string;
    email: string;
    username: string;
  };
  tokens?: {
    AccessToken: string;
    IdToken: string;
    RefreshToken: string;
  };
}

interface AuthErrorResponse {
  success: false;
  error: string;
  message?: string;
}

type AuthResponse = AuthSuccessResponse | AuthErrorResponse;

export const authApi = {
  signUp: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await fetch("/api/auth/cognito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "signUp", email, password }),
    });
    return response.json() as Promise<AuthResponse>;
  },

  confirmSignUp: async (email: string, code: string): Promise<AuthResponse> => {
    const response = await fetch("/api/auth/cognito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "confirmSignUp", email, code }),
    });
    return response.json() as Promise<AuthResponse>;
  },

  signIn: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await fetch("/api/auth/cognito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "signIn", email, password }),
    });
    return response.json() as Promise<AuthResponse>;
  },

  forgotPassword: async (email: string): Promise<AuthResponse> => {
    const response = await fetch("/api/auth/cognito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "forgotPassword", email }),
    });
    return response.json() as Promise<AuthResponse>;
  },

  confirmForgotPassword: async (
    email: string,
    code: string,
    newPassword: string,
  ): Promise<AuthResponse> => {
    const response = await fetch("/api/auth/cognito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "confirmForgotPassword",
        email,
        code,
        newPassword,
      }),
    });
    return response.json() as Promise<AuthResponse>;
  },

  getUser: async (accessToken: string): Promise<AuthResponse> => {
    const response = await fetch("/api/auth/cognito", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "getUser", accessToken }),
    });
    return response.json() as Promise<AuthResponse>;
  },
};
