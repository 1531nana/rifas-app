import { useEffect, useState } from "react";
import { API_URL, request } from "../lib/api.js";

const emptyRaffle = {
  name: "",
  lottery_type: "Loteria de Bogota",
  total_numbers: 100,
  ticket_price: 25000,
  prize_description: "",
  draw_date: "",
  prize_image_url: "",
};

export default function AdminDashboard() {
  const [mode, setMode] = useState("login");
  const [credentials, setCredentials] = useState({ email: "", password: "", full_name: "" });
  const [raffle, setRaffle] = useState(emptyRaffle);
  const [raffles, setRaffles] = useState([]);
  const [message, setMessage] = useState("");

  const isLoggedIn = Boolean(localStorage.getItem("rifas_token"));

  async function loadRaffles() {
    if (!localStorage.getItem("rifas_token")) return;
    const data = await request("/raffles");
    setRaffles(data);
  }

  useEffect(() => {
    loadRaffles().catch(() => setMessage("Inicia sesion para ver tus rifas."));
  }, []);

  async function submitAuth(event) {
    event.preventDefault();
    const endpoint = mode === "register" ? "/auth/register" : "/auth/login";
    const payload =
      mode === "register" ? credentials : { email: credentials.email, password: credentials.password };
    const data = await request(endpoint, { method: "POST", body: JSON.stringify(payload) });
    localStorage.setItem("rifas_token", data.access_token);
    setMessage("Sesion iniciada.");
    await loadRaffles();
  }

  async function submitRaffle(event) {
    event.preventDefault();
    const payload = {
      ...raffle,
      total_numbers: Number(raffle.total_numbers),
      ticket_price: Number(raffle.ticket_price),
      prize_image_url: raffle.prize_image_url || null,
    };
    await request("/raffles", { method: "POST", body: JSON.stringify(payload) });
    setRaffle(emptyRaffle);
    setMessage("Rifa creada.");
    await loadRaffles();
  }

  function logout() {
    localStorage.removeItem("rifas_token");
    setRaffles([]);
    setMessage("Sesion cerrada.");
  }

  return (
    <main className="shell">
      <section className="header">
        <div>
          <p className="eyebrow">Panel del vendedor</p>
          <h1>Gestion de Rifas Digital</h1>
        </div>
        {isLoggedIn && <button onClick={logout}>Cerrar sesion</button>}
      </section>

      {message && <p className="notice">{message}</p>}

      {!isLoggedIn && (
        <section className="panel">
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
            <button type="submit">{mode === "register" ? "Crear cuenta" : "Entrar"}</button>
          </form>
        </section>
      )}

      {isLoggedIn && (
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
              <button type="submit">Crear rifa</button>
            </form>
          </section>

          <section className="panel">
            <h2>Mis rifas</h2>
            <div className="list">
              {raffles.map((item) => (
                <article key={item.id} className="raffle-row">
                  <strong>{item.name}</strong>
                  <span>{item.total_numbers} numeros - ${item.ticket_price}</span>
                  <a href={`/r/${item.public_token}`}>Abrir enlace publico</a>
                  <code>{API_URL}/r/{item.public_token}</code>
                </article>
              ))}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
