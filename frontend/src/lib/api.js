const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

import { MENSAJES_VALIDACION, NOMBRES_CAMPO } from "./constants.js";

function parsearMensajeError(detail) {
  if (!detail) return "Error inesperado";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => {
      const campo = NOMBRES_CAMPO[e.loc?.at(-1)] ?? e.loc?.at(-1) ?? "Campo";
      const mensaje = MENSAJES_VALIDACION[e.type]?.(e.ctx) ?? e.msg ?? "Valor inválido";
      return `${campo}: ${mensaje}`;
    }).join(". ");
  }
  return "Error inesperado";
}

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
        const error = new Error(parsearMensajeError(data?.detail));
        error.status = retry.status;
        throw error;
      }
      return data;
    }
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(parsearMensajeError(data?.detail));
    error.status = response.status;
    throw error;
  }
  return data;
}

export async function uploadFile(path, file) {
  const token = localStorage.getItem("rifas_token");
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });

  if (response.status === 401 && localStorage.getItem("rifas_refresh")) {
    const newToken = await attemptRefresh();
    if (newToken) return uploadFile(path, file);
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(parsearMensajeError(data?.detail));
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
