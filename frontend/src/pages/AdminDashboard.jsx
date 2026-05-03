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

function formatDate(value) {
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function AdminDashboard() {
  const [mode, setMode] = useState("login");
  const [token, setToken] = useState(() => localStorage.getItem("rifas_token") ?? "");
  const [credentials, setCredentials] = useState({ email: "", password: "", full_name: "" });
  const [raffle, setRaffle] = useState(emptyRaffle);
  const [raffles, setRaffles] = useState([]);
  const [selectedRaffle, setSelectedRaffle] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const isLoggedIn = Boolean(token);
  const publicOrigin = window.location.origin;
  const selectedProgress = selectedRaffle
    ? Math.round((selectedRaffle.sold_count / selectedRaffle.total_numbers) * 100)
    : 0;

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
        setMessage("La sesion anterior expiro. Inicia sesion otra vez.");
        return;
      }
      setMessage(error.message);
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
      setToken(data.access_token);
      setMessage("Sesion iniciada.");
      await loadRaffles();
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
      const created = await request("/raffles", { method: "POST", body: JSON.stringify(payload) });
      setRaffle(emptyRaffle);
      setMessage("Rifa creada. Ya puedes compartir el enlace publico.");
      await loadRaffles();
      await loadRaffleDetail(created.id);
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
      await request(`/raffles/${selectedRaffle.id}/reservations/${reservationId}/confirm-cash`, {
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

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      setMessage("Enlace copiado al portapapeles.");
    } catch {
      setMessage("No se pudo copiar automaticamente. Selecciona el enlace manualmente.");
    }
  }

  function logout() {
    clearSession();
    setMessage("Sesion cerrada.");
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Panel del vendedor</p>
          <h1>Gestion de Rifas Digital</h1>
          <p>Crea rifas, comparte enlaces publicos y controla compradores, reservas y pagos desde un solo lugar.</p>
        </div>
        <div className="hero-actions">
          <span className="status-pill online">API activa</span>
          {isLoggedIn && <button className="ghost-button" onClick={logout}>Cerrar sesion</button>}
        </div>
      </section>

      {message && <p className="notice">{message}</p>}

      {!isLoggedIn && (
        <section className="panel auth-panel">
          <p className="eyebrow">Acceso administrativo</p>
          <h2>{mode === "register" ? "Crear cuenta de vendedor" : "Entrar al panel"}</h2>
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
              <strong>Online</strong>
            </article>
          </section>

          <div className="grid-two">
            <section className="panel">
              <div className="section-head">
                <div>
                  <p className="eyebrow">Configuracion</p>
                  <h2>Nueva rifa</h2>
                </div>
              </div>
              <form onSubmit={submitRaffle} className="form">
                <input placeholder="Nombre" value={raffle.name} onChange={(e) => setRaffle({ ...raffle, name: e.target.value })} />
                <input placeholder="Tipo de loteria" value={raffle.lottery_type} onChange={(e) => setRaffle({ ...raffle, lottery_type: e.target.value })} />
                <input type="number" placeholder="Cantidad de numeros" value={raffle.total_numbers} onChange={(e) => setRaffle({ ...raffle, total_numbers: e.target.value })} />
                <input type="number" placeholder="Valor boleta" value={raffle.ticket_price} onChange={(e) => setRaffle({ ...raffle, ticket_price: e.target.value })} />
                <textarea placeholder="Descripcion del premio" value={raffle.prize_description} onChange={(e) => setRaffle({ ...raffle, prize_description: e.target.value })} />
                <input type="datetime-local" value={raffle.draw_date} onChange={(e) => setRaffle({ ...raffle, draw_date: e.target.value })} />
                <input placeholder="URL imagen premio opcional" value={raffle.prize_image_url} onChange={(e) => setRaffle({ ...raffle, prize_image_url: e.target.value })} />
                <button type="submit" disabled={loading}>{loading ? "Guardando..." : "Crear rifa"}</button>
              </form>
            </section>

            <section className="panel">
              <div className="section-head">
                <div>
                  <p className="eyebrow">Operacion</p>
                  <h2>Mis rifas</h2>
                </div>
              </div>
              <div className="raffle-list">
                {raffles.length === 0 && <p className="muted">Aun no hay rifas. Crea la primera para generar el enlace publico.</p>}
                {raffles.map((item) => (
                  <article key={item.id} className={`raffle-card ${selectedRaffle?.id === item.id ? "active" : ""}`}>
                    <div>
                      <button className="link-button" onClick={() => loadRaffleDetail(item.id)}>
                        {item.name}
                      </button>
                      <p className="muted">{item.total_numbers} numeros - {formatMoney(item.ticket_price)}</p>
                    </div>
                    <div className="card-actions">
                      <a className="small-button" href={`/r/${item.public_token}`}>Vista publica</a>
                      <button className="small-button secondary" onClick={() => copyText(`${publicOrigin}/r/${item.public_token}`)}>
                        Copiar enlace
                      </button>
                    </div>
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
                  <p className="muted">Sorteo: {formatDate(selectedRaffle.draw_date)}</p>
                </div>
                <div className="stack-actions">
                  <a className="small-button" href={`/r/${selectedRaffle.public_token}`}>Ver como comprador</a>
                  <button className="small-button secondary" onClick={() => copyText(`${publicOrigin}/r/${selectedRaffle.public_token}`)}>
                    Copiar enlace
                  </button>
                </div>
              </div>

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

              <div className="progress-block">
                <div className="progress-label">
                  <span>Progreso de venta pagada</span>
                  <strong>{selectedProgress}%</strong>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${selectedProgress}%` }} />
                </div>
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
                        <td><span className="badge neutral">{reservation.payment_method}</span></td>
                        <td><span className={`badge ${reservation.status}`}>{reservation.status}</span></td>
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
            </section>
          )}
        </>
      )}
    </main>
  );
}
