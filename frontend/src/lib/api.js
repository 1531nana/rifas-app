const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

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

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.detail ?? "Error inesperado");
    error.status = response.status;
    throw error;
  }
  return data;
}

export async function authRequest(path, options = {}) {
  try {
    return await request(path, options);
  } catch (error) {
    if (error.status !== 401) {
      throw error;
    }
    const refreshToken = localStorage.getItem("rifas_refresh_token");
    if (!refreshToken) {
      throw error;
    }
    const refresh = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const refreshData = await refresh.json().catch(() => null);
    if (!refresh.ok) {
      localStorage.removeItem("rifas_token");
      localStorage.removeItem("rifas_refresh_token");
      throw error;
    }
    localStorage.setItem("rifas_token", refreshData.access_token);
    localStorage.setItem("rifas_refresh_token", refreshData.refresh_token);
    return request(path, options);
  }
}

export async function uploadFile(path, file) {
  const token = localStorage.getItem("rifas_token");
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.detail ?? "Error inesperado");
    error.status = response.status;
    throw error;
  }
  return data;
}

export { API_URL };
