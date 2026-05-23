import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  CheckCircle2,
  Clipboard,
  CreditCard,
  Gift,
  LayoutDashboard,
  Link as LinkIcon,
  LogOut,
  PlusCircle,
  RefreshCw,
  Sparkles,
  Ticket,
  Trophy,
  Users,
} from "lucide-react";
import { API_URL, authRequest, request, uploadFile } from "../lib/api.js";

const demoCredentials = {
  email: "demo@rifasapp.com",
  password: "Demo12345",
  full_name: "Cuenta Demo",
};

function datetimeLocal(daysFromNow = 30) {
  const date = new Date(Date.now() + daysFromNow * 24 * 60 * 60 * 1000);
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 16);
}

function blankRaffle() {
  return {
    name: "Rifa Moto Mayo",
    lottery_type: "Loteria de Bogota",
    total_numbers: 100,
    ticket_price: 25000,
    prize_description: "Moto nueva 125cc con papeles al dia",
    draw_date: datetimeLocal(30),
    prize_image_url: "",
  };
}

function formatMoney(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number(value ?? 0));
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  return new Date(value).toLocaleString("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function toDatetimeLocal(value) {
  if (!value) return datetimeLocal();
  const date = new Date(value);
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 16);
}

function statusText(status) {
  const labels = {
    active: "Activa",
    closed: "Cerrada",
    pending: "Pendiente",
    paid: "Pagada",
    expired: "Expirada",
    cancelled: "Cancelada",
    cash: "Efectivo",
    card: "Tarjeta",
    pse: "PSE",
  };
  return labels[status] ?? status;
}

export default function AdminDashboard() {
  const [mode, setMode] = useState("login");
  const [token, setToken] = useState(() => localStorage.getItem("rifas_token") ?? "");
  const [credentials, setCredentials] = useState({ email: "", password: "", full_name: "" });
  const [raffle, setRaffle] = useState(blankRaffle);
  const [imageFile, setImageFile] = useState(null);
  const [editDraft, setEditDraft] = useState(null);
  const [raffles, setRaffles] = useState([]);
  const [selectedRaffle, setSelectedRaffle] = useState(null);
  const [stats, setStats] = useState(null);
  const [buyerFilter, setBuyerFilter] = useState("all");
  const [winnerNumber, setWinnerNumber] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");

  const isLoggedIn = Boolean(token);
  const publicOrigin = window.location.origin;
  const selectedPublicUrl = selectedRaffle ? `${publicOrigin}/r/${selectedRaffle.public_token}` : "";

  const totals = useMemo(() => {
    return raffles.reduce(
      (acc, item) => ({
        raffles: acc.raffles + 1,
        numbers: acc.numbers + item.total_numbers,
        active: acc.active + (item.status === "active" ? 1 : 0),
      }),
      { raffles: 0, numbers: 0, active: 0 },
    );
  }, [raffles]);

  const visibleReservations = useMemo(() => {
    if (!selectedRaffle) return [];
    if (buyerFilter === "all") return selectedRaffle.reservations;
    return selectedRaffle.reservations.filter((reservation) => reservation.status === buyerFilter);
  }, [buyerFilter, selectedRaffle]);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => setApiStatus(response.ok ? "online" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  useEffect(() => {
    if (token) {
      loadRaffles().catch((error) => setMessage(error.message));
    }
  }, [token]);

  function saveSession(data) {
    localStorage.setItem("rifas_token", data.access_token);
    localStorage.setItem("rifas_refresh_token", data.refresh_token);
    setToken(data.access_token);
  }

  function clearSession() {
    localStorage.removeItem("rifas_token");
    localStorage.removeItem("rifas_refresh_token");
    setToken("");
    setRaffles([]);
    setSelectedRaffle(null);
    setStats(null);
    setEditDraft(null);
  }

  async function loadRaffleDetail(raffleId) {
    const [detail, nextStats] = await Promise.all([
      authRequest(`/raffles/${raffleId}`),
      authRequest(`/raffles/${raffleId}/stats`),
    ]);
    setSelectedRaffle(detail);
    setStats(nextStats);
    setEditDraft({
      name: detail.name,
      lottery_type: detail.lottery_type,
      prize_description: detail.prize_description,
      draw_date: toDatetimeLocal(detail.draw_date),
      prize_image_url: detail.prize_image_url ?? "",
    });
    setWinnerNumber("");
  }

  async function loadRaffles(preferredId = selectedRaffle?.id) {
    const data = await authRequest("/raffles");
    setRaffles(data);
    const nextId = preferredId && data.some((item) => item.id === preferredId) ? preferredId : data[0]?.id;
    if (nextId) {
      await loadRaffleDetail(nextId);
    } else {
      setSelectedRaffle(null);
      setStats(null);
      setEditDraft(null);
    }
  }

  async function submitAuth(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const endpoint = mode === "register" ? "/auth/register" : "/auth/login";
      const payload =
        mode === "register" ? credentials : { email: credentials.email, password: credentials.password };
      const data = await request(endpoint, { method: "POST", body: JSON.stringify(payload) });
      saveSession(data);
      setMessage("Sesion iniciada. Ya puedes crear y administrar rifas.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function loginDemo() {
    setLoading(true);
    setMessage("");
    try {
      let data;
      try {
        data = await request("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email: demoCredentials.email, password: demoCredentials.password }),
        });
      } catch (loginError) {
        data = await request("/auth/register", {
          method: "POST",
          body: JSON.stringify(demoCredentials),
        });
      }
      saveSession(data);
      setMessage("Demo lista. Puedes crear datos de prueba o abrir la vista publica.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitRaffle(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const payload = {
        ...raffle,
        total_numbers: Number(raffle.total_numbers),
        ticket_price: Number(raffle.ticket_price),
        prize_image_url: raffle.prize_image_url || null,
      };
      const created = await authRequest("/raffles", { method: "POST", body: JSON.stringify(payload) });
      if (imageFile) {
        await uploadFile(`/raffles/${created.id}/image`, imageFile);
      }
      setRaffle(blankRaffle());
      setImageFile(null);
      setMessage("Rifa creada. Comparte el enlace publico para vender boletas.");
      await loadRaffles(created.id);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitEdit(event) {
    event.preventDefault();
    if (!selectedRaffle || !editDraft) return;
    setLoading(true);
    setMessage("");
    try {
      await authRequest(`/raffles/${selectedRaffle.id}`, {
        method: "PATCH",
        body: JSON.stringify({ ...editDraft, prize_image_url: editDraft.prize_image_url || null }),
      });
      setMessage("Rifa actualizada.");
      await loadRaffles(selectedRaffle.id);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function confirmCash(reservationId) {
    if (!selectedRaffle) return;
    setLoading(true);
    setMessage("");
    try {
      await authRequest(`/raffles/${selectedRaffle.id}/reservations/${reservationId}/confirm-cash`, {
        method: "POST",
      });
      setMessage("Pago en efectivo confirmado. La boleta ya participa en el sorteo.");
      await loadRaffleDetail(selectedRaffle.id);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function registerWinner(event) {
    event.preventDefault();
    if (!selectedRaffle || winnerNumber === "") return;
    setLoading(true);
    setMessage("");
    try {
      await authRequest(`/raffles/${selectedRaffle.id}/winner`, {
        method: "POST",
        body: JSON.stringify({ winner_number: Number(winnerNumber) }),
      });
      setMessage("Ganador registrado. La rifa quedo cerrada.");
      await loadRaffles(selectedRaffle.id);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function createDemoRaffle() {
    setLoading(true);
    setMessage("");
    try {
      const payload = {
        name: `Rifa Demo ${new Date().toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" })}`,
        lottery_type: "Loteria de Boyaca",
        total_numbers: 60,
        ticket_price: 20000,
        prize_description: "Bono de mercado y premio sorpresa para el ganador",
        draw_date: datetimeLocal(21),
        prize_image_url: "",
      };
      const created = await authRequest("/raffles", { method: "POST", body: JSON.stringify(payload) });
      await loadRaffles(created.id);
      setMessage("Rifa demo creada. Ahora puedes generar compradores de prueba.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function seedDemoSales() {
    if (!selectedRaffle) return;
    setLoading(true);
    setMessage("");
    try {
      const publicData = await request(`/r/${selectedRaffle.public_token}`);
      const available = publicData.numbers.filter((item) => item.status === "available").map((item) => item.number);
      if (available.length < 2) {
        setMessage("No hay suficientes numeros libres para generar datos de prueba.");
        return;
      }

      const cashReservation = await request(`/r/${selectedRaffle.public_token}/reserve`, {
        method: "POST",
        body: JSON.stringify({
          number: available[0],
          buyer_name: "Laura Martinez",
          buyer_phone: "+573001112233",
          buyer_email: "laura@example.com",
          payment_method: "cash",
        }),
      });
      await authRequest(`/raffles/${selectedRaffle.id}/reservations/${cashReservation.id}/confirm-cash`, {
        method: "POST",
      });

      const digitalReservation = await request(`/r/${selectedRaffle.public_token}/reserve`, {
        method: "POST",
        body: JSON.stringify({
          number: available[1],
          buyer_name: "Carlos Ruiz",
          buyer_phone: "+573204445566",
          buyer_email: "carlos@example.com",
          payment_method: "card",
        }),
      });
      await request("/webhooks/wompi", {
        method: "POST",
        body: JSON.stringify({
          data: {
            transaction: {
              id: `local-${digitalReservation.id}-${Date.now()}`,
              status: "APPROVED",
              reference: String(digitalReservation.id),
            },
          },
        }),
      });

      await loadRaffleDetail(selectedRaffle.id);
      setMessage("Compradores de prueba generados: uno en efectivo y uno digital pagado.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function copyPublicLink() {
    if (!selectedPublicUrl) return;
    try {
      await navigator.clipboard.writeText(selectedPublicUrl);
      setMessage("Enlace publico copiado.");
    } catch {
      setMessage(selectedPublicUrl);
    }
  }

  function logout() {
    clearSession();
    setMessage("Sesion cerrada.");
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div className="brand-block">
          <div className="brand-mark"><Ticket size={28} /></div>
          <div>
            <p className="eyebrow">Panel del vendedor</p>
            <h1>Rifas App</h1>
            <p className="muted">Administra rifas, ventas, pagos y ganador desde una sola pantalla.</p>
          </div>
        </div>
        <div className="top-actions">
          <span className={`status-pill ${apiStatus}`}>
            <Activity size={15} /> API {apiStatus === "online" ? "activa" : "sin conexion"}
          </span>
          {isLoggedIn && (
            <button className="ghost-button" onClick={logout}>
              <LogOut size={16} /> Salir
            </button>
          )}
        </div>
      </section>

      {message && <p className="notice">{message}</p>}

      {!isLoggedIn && (
        <section className="auth-layout">
          <div className="panel auth-copy">
            <div>
              <p className="eyebrow">Revision rapida</p>
              <h2>Entra con demo o crea tu usuario</h2>
              <p>
                La app queda conectada al backend local. Con el demo puedes crear una rifa, generar compradores,
                abrir la vista publica y simular pagos digitales sin credenciales reales de Wompi.
              </p>
              <button type="button" onClick={loginDemo} disabled={loading}>
                <Sparkles size={17} /> Entrar con demo
              </button>
            </div>
            <div className="preview-board" aria-hidden="true">
              <div className="preview-card large"><Ticket size={24} /><span>Rifa activa</span><strong>84%</strong></div>
              <div className="preview-card"><Users size={22} /><span>Compradores</span></div>
              <div className="preview-card"><CreditCard size={22} /><span>Pagos</span></div>
            </div>
          </div>

          <section className="panel">
            <div className="segmented">
              <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
                Iniciar sesion
              </button>
              <button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
                Crear cuenta
              </button>
            </div>
            <form onSubmit={submitAuth} className="form">
              {mode === "register" && (
                <label>
                  Nombre completo
                  <input
                    required
                    minLength="2"
                    value={credentials.full_name}
                    onChange={(event) => setCredentials({ ...credentials, full_name: event.target.value })}
                  />
                </label>
              )}
              <label>
                Email
                <input
                  required
                  type="email"
                  value={credentials.email}
                  onChange={(event) => setCredentials({ ...credentials, email: event.target.value })}
                />
              </label>
              <label>
                Contrasena
                <input
                  required
                  minLength="8"
                  type="password"
                  value={credentials.password}
                  onChange={(event) => setCredentials({ ...credentials, password: event.target.value })}
                />
              </label>
              <button type="submit" disabled={loading}>
                <CheckCircle2 size={17} /> {mode === "register" ? "Crear cuenta" : "Entrar"}
              </button>
            </form>
          </section>
        </section>
      )}

      {isLoggedIn && (
        <>
          <section className="metrics">
            <article>
              <Ticket size={20} />
              <span>Rifas</span>
              <strong>{totals.raffles}</strong>
            </article>
            <article>
              <Activity size={20} />
              <span>Activas</span>
              <strong>{totals.active}</strong>
            </article>
            <article>
              <LayoutDashboard size={20} />
              <span>Numeros</span>
              <strong>{totals.numbers}</strong>
            </article>
            <article>
              <CreditCard size={20} />
              <span>Recaudado seleccionado</span>
              <strong>{formatMoney(stats?.total_raised ?? selectedRaffle?.paid_total ?? 0)}</strong>
            </article>
          </section>

          <div className="workspace-grid">
            <aside className="panel side-panel">
              <div className="section-head">
                <div>
                  <p className="eyebrow">Nueva venta</p>
                  <h2><PlusCircle size={19} /> Crear rifa</h2>
                </div>
              </div>
              <form onSubmit={submitRaffle} className="form">
                <label>
                  Nombre
                  <input required value={raffle.name} onChange={(e) => setRaffle({ ...raffle, name: e.target.value })} />
                </label>
                <label>
                  Loteria
                  <input required value={raffle.lottery_type} onChange={(e) => setRaffle({ ...raffle, lottery_type: e.target.value })} />
                </label>
                <div className="split-fields">
                  <label>
                    Numeros
                    <input required min="10" max="10000" type="number" value={raffle.total_numbers} onChange={(e) => setRaffle({ ...raffle, total_numbers: e.target.value })} />
                  </label>
                  <label>
                    Valor
                    <input required min="1" type="number" value={raffle.ticket_price} onChange={(e) => setRaffle({ ...raffle, ticket_price: e.target.value })} />
                  </label>
                </div>
                <label>
                  Premio
                  <textarea required minLength="5" value={raffle.prize_description} onChange={(e) => setRaffle({ ...raffle, prize_description: e.target.value })} />
                </label>
                <label>
                  Fecha del sorteo
                  <input required type="datetime-local" value={raffle.draw_date} onChange={(e) => setRaffle({ ...raffle, draw_date: e.target.value })} />
                </label>
                <label>
                  URL imagen opcional
                  <input value={raffle.prize_image_url} onChange={(e) => setRaffle({ ...raffle, prize_image_url: e.target.value })} />
                </label>
                <label>
                  Subir imagen
                  <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => setImageFile(e.target.files?.[0] ?? null)} />
                </label>
                <button type="submit" disabled={loading}><PlusCircle size={17} /> Crear rifa</button>
              </form>

              <div className="divider" />
              <div className="section-head tight">
                <div>
                  <p className="eyebrow">Listado</p>
                  <h2>Mis rifas</h2>
                </div>
                <button type="button" className="ghost-button" onClick={createDemoRaffle} disabled={loading}>
                  <Sparkles size={16} /> Demo
                </button>
              </div>
              <div className="raffle-list">
                {raffles.length === 0 && <p className="empty-state">Crea una rifa o usa el boton Demo.</p>}
                {raffles.map((item) => (
                  <button
                    type="button"
                    key={item.id}
                    className={`raffle-card ${selectedRaffle?.id === item.id ? "active" : ""}`}
                    onClick={() => loadRaffleDetail(item.id)}
                  >
                    <strong>{item.name}</strong>
                    <span>{statusText(item.status)} - {item.total_numbers} numeros</span>
                    <small>{formatMoney(item.ticket_price)} por boleta</small>
                  </button>
                ))}
              </div>
            </aside>

            <section className="main-stack">
              {!selectedRaffle && (
                <section className="panel empty-panel">
                  <h2>No hay una rifa seleccionada</h2>
                  <p className="muted">Crea una rifa o usa la demo para revisar el flujo completo.</p>
                </section>
              )}

              {selectedRaffle && (
                <>
                  <section className="panel detail-panel">
                    <div className="detail-hero">
                      <div>
                        <p className="eyebrow">{selectedRaffle.lottery_type}</p>
                        <h2><Gift size={20} /> {selectedRaffle.name}</h2>
                        <p>{selectedRaffle.prize_description}</p>
                        <p className="muted">Sorteo: {formatDate(selectedRaffle.draw_date)}</p>
                      </div>
                      <span className={`status-pill ${selectedRaffle.status}`}>{statusText(selectedRaffle.status)}</span>
                    </div>

                    <div className="share-row">
                      <code>{selectedPublicUrl}</code>
                      <button type="button" className="ghost-button" onClick={copyPublicLink}>
                        <Clipboard size={16} /> Copiar
                      </button>
                      <a className="button-link" href={`/r/${selectedRaffle.public_token}`}>
                        <ArrowUpRight size={16} /> Abrir publica
                      </a>
                    </div>

                    {selectedRaffle.status === "closed" && (
                      <p className="notice">Rifa cerrada. Numero ganador: {selectedRaffle.winner_number}</p>
                    )}

                    <div className="metrics compact">
                      <article>
                        <CheckCircle2 size={20} />
                        <span>Pagadas</span>
                        <strong>{selectedRaffle.sold_count}</strong>
                      </article>
                      <article>
                        <Ticket size={20} />
                        <span>Reservadas</span>
                        <strong>{selectedRaffle.reserved_count}</strong>
                      </article>
                      <article>
                        <LayoutDashboard size={20} />
                        <span>Disponibles</span>
                        <strong>{selectedRaffle.available_count}</strong>
                      </article>
                      <article>
                        <Trophy size={20} />
                        <span>Vendido</span>
                        <strong>{Math.round(stats?.percentage_sold ?? 0)}%</strong>
                      </article>
                    </div>
                    <div className="progress-track">
                      <span style={{ width: `${Math.min(100, Math.round(stats?.percentage_sold ?? 0))}%` }} />
                    </div>

                    <div className="action-row">
                      <button type="button" onClick={seedDemoSales} disabled={loading || selectedRaffle.status !== "active"}>
                        <Users size={17} /> Generar compradores demo
                      </button>
                      <button type="button" className="ghost-button" onClick={() => loadRaffleDetail(selectedRaffle.id)} disabled={loading}>
                        <RefreshCw size={16} /> Actualizar datos
                      </button>
                    </div>
                  </section>

                  {editDraft && selectedRaffle.status === "active" && (
                    <section className="panel">
                      <div className="section-head">
                        <div>
                          <p className="eyebrow">Edicion</p>
                          <h2><LinkIcon size={19} /> Ajustes de la rifa</h2>
                        </div>
                      </div>
                      <form onSubmit={submitEdit} className="form dense-form">
                        <label>
                          Nombre
                          <input required value={editDraft.name} onChange={(e) => setEditDraft({ ...editDraft, name: e.target.value })} />
                        </label>
                        <label>
                          Loteria
                          <input required value={editDraft.lottery_type} onChange={(e) => setEditDraft({ ...editDraft, lottery_type: e.target.value })} />
                        </label>
                        <label className="wide-field">
                          Premio
                          <textarea required value={editDraft.prize_description} onChange={(e) => setEditDraft({ ...editDraft, prize_description: e.target.value })} />
                        </label>
                        <label>
                          Fecha del sorteo
                          <input required type="datetime-local" value={editDraft.draw_date} onChange={(e) => setEditDraft({ ...editDraft, draw_date: e.target.value })} />
                        </label>
                        <label>
                          URL imagen
                          <input value={editDraft.prize_image_url} onChange={(e) => setEditDraft({ ...editDraft, prize_image_url: e.target.value })} />
                        </label>
                        <button type="submit" disabled={loading}><CheckCircle2 size={17} /> Guardar cambios</button>
                      </form>
                    </section>
                  )}

                  <section className="panel">
                    <div className="section-head">
                      <div>
                        <p className="eyebrow">Compradores</p>
                        <h2><Users size={19} /> Reservas y pagos</h2>
                      </div>
                      {selectedRaffle.status === "active" && (
                        <form onSubmit={registerWinner} className="winner-form">
                          <input
                            type="number"
                            min="0"
                            max={selectedRaffle.total_numbers - 1}
                            placeholder="Numero ganador"
                            value={winnerNumber}
                            onChange={(event) => setWinnerNumber(event.target.value)}
                          />
                          <button type="submit" disabled={loading}><Trophy size={17} /> Cerrar con ganador</button>
                        </form>
                      )}
                    </div>

                    <div className="filters">
                      {["all", "pending", "paid", "expired", "cancelled"].map((filter) => (
                        <button
                          type="button"
                          key={filter}
                          className={buyerFilter === filter ? "active" : ""}
                          onClick={() => setBuyerFilter(filter)}
                        >
                          {filter === "all" ? "Todos" : statusText(filter)}
                        </button>
                      ))}
                    </div>

                    <div className="table-wrap">
                      <table>
                        <thead>
                          <tr>
                            <th>Numero</th>
                            <th>Comprador</th>
                            <th>Celular</th>
                            <th>Metodo</th>
                            <th>Estado</th>
                            <th>Accion</th>
                          </tr>
                        </thead>
                        <tbody>
                          {visibleReservations.length === 0 && (
                            <tr>
                              <td colSpan="6">Sin compradores en este filtro.</td>
                            </tr>
                          )}
                          {visibleReservations.map((reservation) => (
                            <tr key={reservation.id}>
                              <td>{reservation.number.toString().padStart(2, "0")}</td>
                              <td>{reservation.buyer_name}</td>
                              <td>{reservation.buyer_phone}</td>
                              <td>{statusText(reservation.payment_method)}</td>
                              <td><span className={`mini-status ${reservation.status}`}>{statusText(reservation.status)}</span></td>
                              <td>
                                {reservation.payment_method === "cash" && reservation.status === "pending" ? (
                                  <button type="button" onClick={() => confirmCash(reservation.id)} disabled={loading}>
                                    <CheckCircle2 size={16} /> Confirmar efectivo
                                  </button>
                                ) : (
                                  <span className="muted">Listo</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </section>
                </>
              )}
            </section>
          </div>
        </>
      )}
    </main>
  );
}
