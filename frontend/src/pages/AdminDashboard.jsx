import { useEffect, useMemo, useState } from "react";
import { API_URL, request } from "../lib/api.js";

const emptyRaffle = {
  name: "Rifa Moto Mayo",
  lottery_type: "Loteria de Bogota",
  total_numbers: 100,
  ticket_price: 25000,
  prize_description: "Moto nueva 125cc con papeles al dia",
  draw_date: "",
  prize_image_url: "",
};

function formatMoney(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function AdminDashboard() {
  const [mode, setMode] = useState("login");
  const [token, setToken] = useState(() => localStorage.getItem("rifas_token") ?? "");
  const [credentials, setCredentials] = useState({ email: "", password: "", full_name: "" });
  const [raffle, setRaffle] = useState(emptyRaffle);
  const [raffles, setRaffles] = useState([]);
  const [selectedRaffle, setSelectedRaffle] = useState(null);
  const [editingRaffle, setEditingRaffle] = useState(null);
  const [message, setMessage] = useState({ text: "", error: false });
  const [loading, setLoading] = useState(false);

  function setOk(text) { setMessage({ text, error: false }); }
  function setErr(text) { setMessage({ text, error: true }); }

  const isLoggedIn = Boolean(token);
  const publicOrigin = window.location.origin;

  const totals = useMemo(() => {
    return raffles.reduce(
      (acc, item) => ({
        raffles: acc.raffles + 1,
        numbers: acc.numbers + item.total_numbers,
      }),
      { raffles: 0, numbers: 0 },
    );
  }, [raffles]);

  function clearSession() {
    localStorage.removeItem("rifas_token");
    localStorage.removeItem("rifas_refresh");
    setToken("");
    setRaffles([]);
    setSelectedRaffle(null);
  }

  async function loadRaffles() {
    if (!localStorage.getItem("rifas_token")) return;
    try {
      const data = await request("/raffles");
      setRaffles(data);
      if (data.length > 0) {
        await loadRaffleDetail(data[0].id);
      } else {
        setSelectedRaffle(null);
      }
    } catch (error) {
      if (error.status === 401) {
        clearSession();
        setErr("La sesión anterior expiró. Inicia sesión otra vez.");
        return;
      }
      setErr(error.message);
    }
  }

  async function loadRaffleDetail(raffleId) {
    const data = await request(`/raffles/${raffleId}`);
    setSelectedRaffle(data);
  }

  useEffect(() => {
    loadRaffles();
  }, []);

  async function submitAuth(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const endpoint = mode === "register" ? "/auth/register" : "/auth/login";
      const payload =
        mode === "register" ? credentials : { email: credentials.email, password: credentials.password };
      const data = await request(endpoint, { method: "POST", body: JSON.stringify(payload) });
      localStorage.setItem("rifas_token", data.access_token);
      localStorage.setItem("rifas_refresh", data.refresh_token);
      setToken(data.access_token);
      setOk("Sesión iniciada.");
      await loadRaffles();
    } catch (error) {
      setErr(error.message);
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
      const created = await request("/raffles", { method: "POST", body: JSON.stringify(payload) });
      setRaffle(emptyRaffle);
      setOk("Rifa creada. Ya puedes compartir el enlace público.");
      await loadRaffles();
      await loadRaffleDetail(created.id);
    } catch (error) {
      setErr(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function confirmCash(reservationId) {
    if (!selectedRaffle) return;
    setLoading(true);
    setMessage("");
    try {
      await request(`/raffles/${selectedRaffle.id}/reservations/${reservationId}/confirm-cash`, {
        method: "POST",
      });
      setOk("Pago en efectivo confirmado. La boleta ya participa en el sorteo.");
      await loadRaffleDetail(selectedRaffle.id);
    } catch (error) {
      setErr(error.message);
    } finally {
      setLoading(false);
    }
  }

  function startEdit(raffleData) {
    const drawDate = raffleData.draw_date ? raffleData.draw_date.substring(0, 16) : "";
    setEditingRaffle({
      name: raffleData.name,
      lottery_type: raffleData.lottery_type,
      total_numbers: raffleData.total_numbers,
      ticket_price: raffleData.ticket_price,
      prize_description: raffleData.prize_description,
      draw_date: drawDate,
      prize_image_url: raffleData.prize_image_url ?? "",
    });
  }

  function cancelEdit() {
    setEditingRaffle(null);
  }

  async function submitEdit(event) {
    event.preventDefault();
    if (!selectedRaffle || !editingRaffle) return;
    setLoading(true);
    setMessage("");
    try {
      const payload = {
        ...editingRaffle,
        total_numbers: Number(editingRaffle.total_numbers),
        ticket_price: Number(editingRaffle.ticket_price),
        prize_image_url: editingRaffle.prize_image_url || null,
      };
      await request(`/raffles/${selectedRaffle.id}`, { method: "PATCH", body: JSON.stringify(payload) });
      setEditingRaffle(null);
      setOk("Rifa actualizada correctamente.");
      await loadRaffleDetail(selectedRaffle.id);
      await loadRaffles();
    } catch (error) {
      setErr(error.message);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearSession();
    setOk("Sesión cerrada.");
  }

  return (
    <main className="shell">
      <section className="header">
        <div>
          <p className="eyebrow">Panel del vendedor</p>
          <h1>Gestion de Rifas Digital</h1>
          <p className="muted">Crea rifas, comparte enlaces publicos y controla pagos pendientes.</p>
        </div>
        {isLoggedIn && <button onClick={logout}>Cerrar sesion</button>}
      </section>

      {message.text && (
        <p className={message.error ? "notice-error" : "notice"}>{message.text}</p>
      )}

      {!isLoggedIn && (
        <section className="panel auth-panel">
          <div className="tabs">
            <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
              Iniciar sesion
            </button>
            <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
              Crear cuenta
            </button>
          </div>
          <form onSubmit={submitAuth} className="form">
            {mode === "register" && (
              <input
                placeholder="Nombre completo"
                value={credentials.full_name}
                onChange={(event) => setCredentials({ ...credentials, full_name: event.target.value })}
              />
            )}
            <input
              placeholder="Email"
              type="email"
              value={credentials.email}
              onChange={(event) => setCredentials({ ...credentials, email: event.target.value })}
            />
            <input
              placeholder="Contrasena"
              type="password"
              value={credentials.password}
              onChange={(event) => setCredentials({ ...credentials, password: event.target.value })}
            />
            <button type="submit" disabled={loading}>
              {mode === "register" ? "Crear cuenta" : "Entrar"}
            </button>
          </form>
        </section>
      )}

      {isLoggedIn && (
        <>
          <section className="metrics">
            <article>
              <span>Rifas creadas</span>
              <strong>{totals.raffles}</strong>
            </article>
            <article>
              <span>Numeros configurados</span>
              <strong>{totals.numbers}</strong>
            </article>
            <article>
              <span>API</span>
              <strong>Activa</strong>
            </article>
          </section>

          <div className="grid-two">
            <section className="panel">
              <h2>Nueva rifa</h2>
              <form onSubmit={submitRaffle} className="form">
                <div className="field">
                  <label>Nombre de la rifa</label>
                  <input value={raffle.name} onChange={(e) => setRaffle({ ...raffle, name: e.target.value })} />
                </div>
                <div className="field">
                  <label>Tipo de lotería</label>
                  <input value={raffle.lottery_type} onChange={(e) => setRaffle({ ...raffle, lottery_type: e.target.value })} />
                </div>
                <div className="field">
                  <label>Cantidad de números</label>
                  <input type="number" value={raffle.total_numbers} onChange={(e) => setRaffle({ ...raffle, total_numbers: e.target.value })} />
                </div>
                <div className="field">
                  <label>Valor por boleta (COP)</label>
                  <input type="number" value={raffle.ticket_price} onChange={(e) => setRaffle({ ...raffle, ticket_price: e.target.value })} />
                </div>
                <div className="field">
                  <label>Descripción del premio</label>
                  <textarea value={raffle.prize_description} onChange={(e) => setRaffle({ ...raffle, prize_description: e.target.value })} />
                </div>
                <div className="field">
                  <label>Fecha del sorteo</label>
                  <input type="datetime-local" value={raffle.draw_date} onChange={(e) => setRaffle({ ...raffle, draw_date: e.target.value })} />
                </div>
                <div className="field">
                  <label>URL imagen del premio (opcional)</label>
                  <input value={raffle.prize_image_url} onChange={(e) => setRaffle({ ...raffle, prize_image_url: e.target.value })} />
                </div>
                <button type="submit" disabled={loading}>Crear rifa</button>
              </form>
            </section>

            <section className="panel">
              <h2>Mis rifas</h2>
              <div className="list">
                {raffles.length === 0 && <p className="muted">Aun no hay rifas. Crea la primera para generar el enlace publico.</p>}
                {raffles.map((item) => (
                  <article key={item.id} className="raffle-row">
                    <button className="link-button" onClick={() => loadRaffleDetail(item.id)}>
                      {item.name}
                    </button>
                    <span>{item.total_numbers} numeros - {formatMoney(item.ticket_price)}</span>
                    <a href={`/r/${item.public_token}`}>Abrir vista publica</a>
                    <code>{publicOrigin}/r/{item.public_token}</code>
                  </article>
                ))}
              </div>
            </section>
          </div>

          {selectedRaffle && (
            <section className="panel detail-panel">
              <div className="section-head">
                <div>
                  <p className="eyebrow">Detalle de rifa</p>
                  <h2>{selectedRaffle.name}</h2>
                  <p className="muted">{selectedRaffle.prize_description}</p>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={() => startEdit(selectedRaffle)}>Editar</button>
                  <a href={`/r/${selectedRaffle.public_token}`}>Ver como comprador</a>
                </div>
              </div>

              {editingRaffle ? (
                <form onSubmit={submitEdit} className="form">
                  <div className="field">
                    <label>Nombre de la rifa</label>
                    <input value={editingRaffle.name} onChange={(e) => setEditingRaffle({ ...editingRaffle, name: e.target.value })} />
                  </div>
                  <div className="field">
                    <label>Tipo de lotería</label>
                    <input value={editingRaffle.lottery_type} onChange={(e) => setEditingRaffle({ ...editingRaffle, lottery_type: e.target.value })} />
                  </div>
                  <div className="field">
                    <label>Cantidad de números</label>
                    <input
                      type="number"
                      value={editingRaffle.total_numbers}
                      onChange={(e) => setEditingRaffle({ ...editingRaffle, total_numbers: e.target.value })}
                      disabled={selectedRaffle.sold_count > 0 || selectedRaffle.reserved_count > 0}
                    />
                  </div>
                  <div className="field">
                    <label>Valor por boleta (COP)</label>
                    <input
                      type="number"
                      value={editingRaffle.ticket_price}
                      onChange={(e) => setEditingRaffle({ ...editingRaffle, ticket_price: e.target.value })}
                      disabled={selectedRaffle.sold_count > 0 || selectedRaffle.reserved_count > 0}
                    />
                  </div>
                  <div className="field">
                    <label>Descripción del premio</label>
                    <textarea value={editingRaffle.prize_description} onChange={(e) => setEditingRaffle({ ...editingRaffle, prize_description: e.target.value })} />
                  </div>
                  <div className="field">
                    <label>Fecha del sorteo</label>
                    <input type="datetime-local" value={editingRaffle.draw_date} onChange={(e) => setEditingRaffle({ ...editingRaffle, draw_date: e.target.value })} />
                  </div>
                  <div className="field">
                    <label>URL imagen del premio (opcional)</label>
                    <input value={editingRaffle.prize_image_url} onChange={(e) => setEditingRaffle({ ...editingRaffle, prize_image_url: e.target.value })} />
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button type="submit" disabled={loading}>Guardar cambios</button>
                    <button type="button" onClick={cancelEdit}>Cancelar</button>
                  </div>
                  {selectedRaffle.sold_count > 0 || selectedRaffle.reserved_count > 0 ? (
                    <p className="muted">Precio y cantidad bloqueados por reservas activas.</p>
                  ) : null}
                </form>
              ) : (
                <>
                  <div className="metrics compact">
                    <article>
                      <span>Pagadas</span>
                      <strong>{selectedRaffle.sold_count}</strong>
                    </article>
                    <article>
                      <span>Reservadas</span>
                      <strong>{selectedRaffle.reserved_count}</strong>
                    </article>
                    <article>
                      <span>Disponibles</span>
                      <strong>{selectedRaffle.available_count}</strong>
                    </article>
                    <article>
                      <span>Recaudado</span>
                      <strong>{formatMoney(selectedRaffle.paid_total)}</strong>
                    </article>
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
                        {selectedRaffle.reservations.length === 0 && (
                          <tr>
                            <td colSpan="6">Sin compradores registrados todavia.</td>
                          </tr>
                        )}
                        {selectedRaffle.reservations.map((reservation) => (
                          <tr key={reservation.id}>
                            <td>{reservation.number}</td>
                            <td>{reservation.buyer_name}</td>
                            <td>{reservation.buyer_phone}</td>
                            <td>{reservation.payment_method}</td>
                            <td>
                              <span className={`badge badge-${reservation.status}`}>
                                {{ pending: "Pendiente", paid: "Pagado", expired: "Expirado" }[reservation.status] ?? reservation.status}
                              </span>
                            </td>
                            <td>
                              {reservation.payment_method === "cash" && reservation.status === "pending" ? (
                                <button onClick={() => confirmCash(reservation.id)} disabled={loading}>
                                  Confirmar efectivo
                                </button>
                              ) : (
                                <span className="muted">Sin accion</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </section>
          )}
        </>
      )}
    </main>
  );
}
