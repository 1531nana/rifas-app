import { useEffect, useMemo, useState } from "react";
import { authRequest, request, uploadFile } from "../lib/api.js";

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
  const [imageFile, setImageFile] = useState(null);
  const [editDraft, setEditDraft] = useState(null);
  const [raffles, setRaffles] = useState([]);
  const [selectedRaffle, setSelectedRaffle] = useState(null);
  const [buyerFilter, setBuyerFilter] = useState("all");
  const [winnerNumber, setWinnerNumber] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

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
    localStorage.removeItem("rifas_refresh_token");
    setToken("");
    setRaffles([]);
    setSelectedRaffle(null);
    setEditDraft(null);
  }

  async function loadRaffles() {
    if (!localStorage.getItem("rifas_token")) return;
    try {
      const data = await authRequest("/raffles");
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
    const data = await authRequest(`/raffles/${raffleId}`);
    setSelectedRaffle(data);
    setEditDraft({
      name: data.name,
      lottery_type: data.lottery_type,
      prize_description: data.prize_description,
      draw_date: data.draw_date.slice(0, 16),
      prize_image_url: data.prize_image_url ?? "",
    });
    setWinnerNumber("");
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
      localStorage.setItem("rifas_refresh_token", data.refresh_token);
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
      const created = await authRequest("/raffles", { method: "POST", body: JSON.stringify(payload) });
      if (imageFile) {
        await uploadFile(`/raffles/${created.id}/image`, imageFile);
      }
      setRaffle(emptyRaffle);
      setImageFile(null);
      setMessage("Rifa creada. Ya puedes compartir el enlace publico.");
      await loadRaffles();
      await loadRaffleDetail(created.id);
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
      await loadRaffles();
      await loadRaffleDetail(selectedRaffle.id);
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
      setMessage("Ganador registrado y rifa cerrada.");
      await loadRaffles();
      await loadRaffleDetail(selectedRaffle.id);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearSession();
    setMessage("Sesion cerrada.");
  }

  const visibleReservations = useMemo(() => {
    if (!selectedRaffle) return [];
    if (buyerFilter === "all") return selectedRaffle.reservations;
    return selectedRaffle.reservations.filter((reservation) => reservation.status === buyerFilter);
  }, [buyerFilter, selectedRaffle]);

  return (
    <main className="shell min-h-screen">
      <section className="header">
        <div>
          <p className="eyebrow">Panel del vendedor</p>
          <h1>Gestion de Rifas Digital</h1>
          <p className="muted">Crea rifas, comparte enlaces publicos y controla pagos pendientes.</p>
        </div>
        {isLoggedIn && <button onClick={logout}>Cerrar sesion</button>}
      </section>

      {message && <p className="notice">{message}</p>}

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
                <input placeholder="Nombre" value={raffle.name} onChange={(e) => setRaffle({ ...raffle, name: e.target.value })} />
                <input placeholder="Tipo de loteria" value={raffle.lottery_type} onChange={(e) => setRaffle({ ...raffle, lottery_type: e.target.value })} />
                <input type="number" placeholder="Cantidad de numeros" value={raffle.total_numbers} onChange={(e) => setRaffle({ ...raffle, total_numbers: e.target.value })} />
                <input type="number" placeholder="Valor boleta" value={raffle.ticket_price} onChange={(e) => setRaffle({ ...raffle, ticket_price: e.target.value })} />
                <textarea placeholder="Descripcion del premio" value={raffle.prize_description} onChange={(e) => setRaffle({ ...raffle, prize_description: e.target.value })} />
                <input type="datetime-local" value={raffle.draw_date} onChange={(e) => setRaffle({ ...raffle, draw_date: e.target.value })} />
                <input placeholder="URL imagen premio opcional" value={raffle.prize_image_url} onChange={(e) => setRaffle({ ...raffle, prize_image_url: e.target.value })} />
                <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => setImageFile(e.target.files?.[0] ?? null)} />
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
                  {selectedRaffle.status === "closed" && (
                    <p className="notice">Rifa cerrada. Numero ganador: {selectedRaffle.winner_number}</p>
                  )}
                </div>
                <a href={`/r/${selectedRaffle.public_token}`}>Ver como comprador</a>
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

              {editDraft && selectedRaffle.status === "active" && (
                <form onSubmit={submitEdit} className="form inline-form">
                  <input placeholder="Nombre" value={editDraft.name} onChange={(e) => setEditDraft({ ...editDraft, name: e.target.value })} />
                  <input placeholder="Tipo de loteria" value={editDraft.lottery_type} onChange={(e) => setEditDraft({ ...editDraft, lottery_type: e.target.value })} />
                  <textarea placeholder="Descripcion del premio" value={editDraft.prize_description} onChange={(e) => setEditDraft({ ...editDraft, prize_description: e.target.value })} />
                  <input type="datetime-local" value={editDraft.draw_date} onChange={(e) => setEditDraft({ ...editDraft, draw_date: e.target.value })} />
                  <input placeholder="URL imagen premio opcional" value={editDraft.prize_image_url} onChange={(e) => setEditDraft({ ...editDraft, prize_image_url: e.target.value })} />
                  <button type="submit" disabled={loading}>Guardar cambios</button>
                </form>
              )}

              {selectedRaffle.status === "active" && (
                <form onSubmit={registerWinner} className="winner-form">
                  <input
                    type="number"
                    placeholder="Numero ganador"
                    value={winnerNumber}
                    onChange={(event) => setWinnerNumber(event.target.value)}
                  />
                  <button type="submit" disabled={loading}>Registrar ganador</button>
                </form>
              )}

              <div className="filters">
                <button className={buyerFilter === "all" ? "active" : ""} onClick={() => setBuyerFilter("all")}>Todos</button>
                <button className={buyerFilter === "pending" ? "active" : ""} onClick={() => setBuyerFilter("pending")}>Pendientes</button>
                <button className={buyerFilter === "paid" ? "active" : ""} onClick={() => setBuyerFilter("paid")}>Pagados</button>
                <button className={buyerFilter === "expired" ? "active" : ""} onClick={() => setBuyerFilter("expired")}>Expirados</button>
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
                        <td colSpan="6">Sin compradores registrados todavia.</td>
                      </tr>
                    )}
                    {visibleReservations.map((reservation) => (
                      <tr key={reservation.id}>
                        <td>{reservation.number}</td>
                        <td>{reservation.buyer_name}</td>
                        <td>{reservation.buyer_phone}</td>
                        <td>{reservation.payment_method}</td>
                        <td>{reservation.status}</td>
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
