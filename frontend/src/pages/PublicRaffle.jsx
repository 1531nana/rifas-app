import { useEffect, useMemo, useState } from "react";
import { request } from "../lib/api.js";

export default function PublicRaffle({ token }) {
  const [raffle, setRaffle] = useState(null);
  const [selected, setSelected] = useState(null);
  const [buyer, setBuyer] = useState({ buyer_name: "", buyer_phone: "", buyer_email: "", payment_method: "cash" });
  const [message, setMessage] = useState("");

  const selectedState = useMemo(
    () => raffle?.numbers?.find((item) => item.number === selected)?.status,
    [raffle, selected],
  );

  async function loadRaffle() {
    const data = await request(`/r/${token}`);
    setRaffle(data);
  }

  useEffect(() => {
    loadRaffle().catch((error) => setMessage(error.message));
  }, [token]);

  async function reserve(event) {
    event.preventDefault();
    await request(`/r/${token}/reserve`, {
      method: "POST",
      body: JSON.stringify({ ...buyer, buyer_email: buyer.buyer_email || null, number: selected }),
    });
    setMessage("Numero reservado. Completa el pago para que la boleta participe.");
    setSelected(null);
    setBuyer({ buyer_name: "", buyer_phone: "", buyer_email: "", payment_method: "cash" });
    await loadRaffle();
  }

  if (!raffle) {
    return <main className="shell">{message || "Cargando rifa..."}</main>;
  }

  return (
    <main className="shell">
      <section className="public-hero">
        <div>
          <p className="eyebrow">{raffle.lottery_type}</p>
          <h1>{raffle.name}</h1>
          <p>{raffle.prize_description}</p>
          <strong>${raffle.ticket_price} por boleta</strong>
        </div>
        {raffle.prize_image_url && <img src={raffle.prize_image_url} alt={`Premio de ${raffle.name}`} />}
      </section>

      {message && <p className="notice">{message}</p>}

      <section className="panel">
        <h2>Selecciona tu numero</h2>
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

      {selected !== null && selectedState === "available" && (
        <section className="panel">
          <h2>Reservar numero {selected}</h2>
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
        </section>
      )}
    </main>
  );
}
