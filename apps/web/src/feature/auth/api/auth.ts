export const authApi = {
  signUp: async (email: string, password: string) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'signUp', email, password }),
    });
    return response.json();
  },

  confirmSignUp: async (email: string, code: string) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'confirmSignUp', email, code }),
    });
    return response.json();
  },

  signIn: async (email: string, password: string) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'signIn', email, password }),
    });
    return response.json();
  },

  forgotPassword: async (email: string) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'forgotPassword', email }),
    });
    return response.json();
  },

  confirmForgotPassword: async (email: string, code: string, newPassword: string) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'confirmForgotPassword', email, code, newPassword }),
    });
    return response.json();
  },

  getUser: async (accessToken: string) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'getUser', accessToken }),
    });
    return response.json();
  },
};
