import { useEffect, useMemo, useState } from "react";
import { request } from "../lib/api.js";

function formatMoney(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function PublicRaffle({ token }) {
  const [raffle, setRaffle] = useState(null);
  const [selected, setSelected] = useState(null);
  const [buyer, setBuyer] = useState({ buyer_name: "", buyer_phone: "", buyer_email: "", payment_method: "cash" });
  const [message, setMessage] = useState("");

  const selectedState = useMemo(
    () => raffle?.numbers?.find((item) => item.number === selected)?.status,
    [raffle, selected],
  );
  const counts = useMemo(() => {
    if (!raffle) return { available: 0, reserved: 0, sold: 0 };
    return raffle.numbers.reduce(
      (acc, item) => ({ ...acc, [item.status]: acc[item.status] + 1 }),
      { available: 0, reserved: 0, sold: 0 },
    );
  }, [raffle]);

  async function loadRaffle() {
    const data = await request(`/r/${token}`);
    setRaffle(data);
  }

  useEffect(() => {
    loadRaffle().catch((error) => setMessage(error.message));
  }, [token]);

  async function reserve(event) {
    event.preventDefault();
    try {
      await request(`/r/${token}/reserve`, {
        method: "POST",
        body: JSON.stringify({ ...buyer, buyer_email: buyer.buyer_email || null, number: selected }),
      });
      setMessage("Numero reservado. Completa el pago para que la boleta participe.");
      setSelected(null);
      setBuyer({ buyer_name: "", buyer_phone: "", buyer_email: "", payment_method: "cash" });
      await loadRaffle();
    } catch (error) {
      setMessage(error.message);
    }
  }

  if (!raffle) {
    return <main className="app-shell"><section className="panel">{message || "Cargando rifa..."}</section></main>;
  }

  return (
    <main className="app-shell">
      <section className="public-hero">
        <div className="hero-copy">
          <p className="eyebrow">{raffle.lottery_type}</p>
          <h1>{raffle.name}</h1>
          <p>{raffle.prize_description}</p>
          <div className="hero-facts">
            <span>{formatMoney(raffle.ticket_price)} por boleta</span>
            <span>Sorteo: {formatDate(raffle.draw_date)}</span>
          </div>
        </div>
        <div className="prize-visual">
          {raffle.prize_image_url ? (
            <img src={raffle.prize_image_url} alt={`Premio de ${raffle.name}`} />
          ) : (
            <div>
              <span>Premio</span>
              <strong>{raffle.prize_description}</strong>
            </div>
          )}
        </div>
      </section>

      {message && <p className="notice">{message}</p>}

      <section className="metrics compact">
        <article>
          <span>Disponibles</span>
          <strong>{counts.available}</strong>
        </article>
        <article>
          <span>Reservados</span>
          <strong>{counts.reserved}</strong>
        </article>
        <article>
          <span>Vendidos</span>
          <strong>{counts.sold}</strong>
        </article>
      </section>

      <div className="buyer-layout">
        <section className="panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Seleccion de boleta</p>
              <h2>Elige tu numero</h2>
            </div>
            <div className="legend">
              <span><i className="dot available" /> Disponible</span>
              <span><i className="dot reserved" /> Reservado</span>
              <span><i className="dot sold" /> Vendido</span>
            </div>
          </div>
          <div className="number-grid">
            {raffle.numbers.map((item) => (
              <button
                key={item.number}
                className={`number ${item.status} ${selected === item.number ? "selected" : ""}`}
                disabled={item.status !== "available"}
                onClick={() => setSelected(item.number)}
              >
                {item.number.toString().padStart(2, "0")}
              </button>
            ))}
          </div>
        </section>

        <section className="panel checkout-panel">
          {selected === null || selectedState !== "available" ? (
            <>
              <p className="eyebrow">Reserva</p>
              <h2>Selecciona un numero disponible</h2>
              <p className="muted">Cuando lo elijas, aqui aparece el formulario para separar tu boleta.</p>
            </>
          ) : (
            <>
              <p className="eyebrow">Reserva segura</p>
              <h2>Numero {selected.toString().padStart(2, "0")}</h2>
              <form onSubmit={reserve} className="form">
                <input placeholder="Nombre completo" value={buyer.buyer_name} onChange={(e) => setBuyer({ ...buyer, buyer_name: e.target.value })} />
                <input placeholder="Celular" value={buyer.buyer_phone} onChange={(e) => setBuyer({ ...buyer, buyer_phone: e.target.value })} />
                <input placeholder="Email opcional" type="email" value={buyer.buyer_email} onChange={(e) => setBuyer({ ...buyer, buyer_email: e.target.value })} />
                <select value={buyer.payment_method} onChange={(e) => setBuyer({ ...buyer, payment_method: e.target.value })}>
                  <option value="cash">Efectivo</option>
                  <option value="card">Tarjeta</option>
                  <option value="pse">PSE</option>
                </select>
                <p className="muted">Efectivo tiene plazo de 5 dias. Tarjeta y PSE tienen plazo de 48 horas.</p>
                <button type="submit">Confirmar reserva</button>
              </form>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
