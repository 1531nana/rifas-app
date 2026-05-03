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

export { API_URL };
