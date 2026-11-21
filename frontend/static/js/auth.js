/**
 * Authentication Module: Login, Register, Forgot Password, Token Handling
 */

const AuthModule = {
  getToken() {
    return localStorage.getItem("smart_fitness_token");
  },

  setToken(token) {
    localStorage.setItem("smart_fitness_token", token);
  },

  clearToken() {
    localStorage.removeItem("smart_fitness_token");
  },

  async login(email, password) {
    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    return res.json();
  },

  async register(userData) {
    const res = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData)
    });
    return res.json();
  },

  async logout() {
    try {
      await fetch("/api/logout", { method: "POST" });
    } catch (e) {
      console.warn("Logout error:", e);
    }
    this.clearToken();
    window.location.href = "/login";
  }
};

window.AuthModule = AuthModule;
