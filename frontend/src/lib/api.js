const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

let refreshPromise = null;

export async function request(path, options = {}) {
  const token = localStorage.getItem("rifas_token");
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401 && localStorage.getItem("rifas_refresh")) {
    const newToken = await attemptRefresh();
    if (newToken) {
      const retry = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${newToken}`,
          ...options.headers,
        },
      });
      const data = await retry.json().catch(() => null);
      if (!retry.ok) {
        const error = new Error(data?.detail ?? "Error inesperado");
        error.status = retry.status;
        throw error;
      }
      return data;
    }
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.detail ?? "Error inesperado");
    error.status = response.status;
    throw error;
  }
  return data;
}

async function attemptRefresh() {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    const refreshToken = localStorage.getItem("rifas_refresh");
    try {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) {
        localStorage.removeItem("rifas_token");
        localStorage.removeItem("rifas_refresh");
        return null;
      }
      const data = await res.json();
      localStorage.setItem("rifas_token", data.access_token);
      localStorage.setItem("rifas_refresh", data.refresh_token);
      return data.access_token;
    } catch {
      localStorage.removeItem("rifas_token");
      localStorage.removeItem("rifas_refresh");
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export { API_URL };
