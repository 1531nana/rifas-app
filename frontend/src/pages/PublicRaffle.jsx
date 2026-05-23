import React, { useEffect, useMemo, useState } from "react";
import { BadgeDollarSign, CalendarDays, CheckCircle2, CreditCard, Gift, ShieldCheck, Ticket } from "lucide-react";
import { request } from "../lib/api.js";

const emptyBuyer = {
  buyer_name: "",
  buyer_phone: "",
  buyer_email: "",
  payment_method: "cash",
};

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
    dateStyle: "full",
    timeStyle: "short",
  });
}

function numberLabel(number, total) {
  const width = Math.max(String(total - 1).length, 2);
  return String(number).padStart(width, "0");
}

export default function PublicRaffle({ token }) {
  const [raffle, setRaffle] = useState(null);
  const [selected, setSelected] = useState(null);
  const [buyer, setBuyer] = useState(emptyBuyer);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [digitalReservation, setDigitalReservation] = useState(null);
  const [checkout, setCheckout] = useState(null);

  const selectedState = useMemo(
    () => raffle?.numbers?.find((item) => item.number === selected)?.status,
    [raffle, selected],
  );

  const counts = useMemo(() => {
    if (!raffle) return { available: 0, reserved: 0, sold: 0 };
    return raffle.numbers.reduce(
      (acc, item) => ({ ...acc, [item.status]: (acc[item.status] ?? 0) + 1 }),
      { available: 0, reserved: 0, sold: 0 },
    );
  }, [raffle]);

  async function loadRaffle() {
    setLoading(true);
    const data = await request(`/r/${token}`);
    setRaffle(data);
    setLoading(false);
  }

  useEffect(() => {
    loadRaffle().catch((error) => {
      setLoading(false);
      setMessage(error.message);
    });
  }, [token]);

  async function reserve(event) {
    event.preventDefault();
    if (selected === null || selectedState !== "available") {
      setMessage("Selecciona un numero disponible.");
      return;
    }
    setSaving(true);
    setMessage("");
    setDigitalReservation(null);
    setCheckout(null);

    try {
      const reservation = await request(`/r/${token}/reserve`, {
        method: "POST",
        body: JSON.stringify({ ...buyer, buyer_email: buyer.buyer_email || null, number: selected }),
      });

      if (buyer.payment_method === "card" || buyer.payment_method === "pse") {
        const nextCheckout = await request(`/r/${token}/reservations/${reservation.id}/checkout`, { method: "POST" });
        setDigitalReservation(reservation);
        setCheckout(nextCheckout);
        if (!nextCheckout.sandbox) {
          window.location.href = nextCheckout.checkout_url;
          return;
        }
        setMessage("Reserva digital creada. En modo local puedes simular la aprobacion del pago.");
      } else {
        setMessage("Numero reservado. Coordina el pago en efectivo con el organizador. Tienes 5 dias.");
        setBuyer(emptyBuyer);
      }

      setSelected(null);
      await loadRaffle();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  async function simulatePayment() {
    if (!digitalReservation) return;
    setSaving(true);
    setMessage("");
    try {
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
      setMessage("Pago digital aprobado en sandbox. Tu numero ya aparece vendido.");
      setDigitalReservation(null);
      setCheckout(null);
      setBuyer(emptyBuyer);
      await loadRaffle();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <main className="app-shell public-shell">
        <section className="panel empty-panel">Cargando rifa...</section>
      </main>
    );
  }

  if (!raffle) {
    return (
      <main className="app-shell public-shell">
        <section className="panel empty-panel">{message || "Rifa no encontrada"}</section>
      </main>
    );
  }

  return (
    <main className="app-shell public-shell">
      <section className="public-hero">
        <div className="public-copy">
          <div className="public-brand"><Ticket size={22} /> Rifa verificada</div>
          <p className="eyebrow">{raffle.lottery_type}</p>
          <h1>{raffle.name}</h1>
          <p>{raffle.prize_description}</p>
          <div className="hero-facts">
            <strong><BadgeDollarSign size={18} /> {formatMoney(raffle.ticket_price)}</strong>
            <span><CalendarDays size={17} /> Sorteo: {formatDate(raffle.draw_date)}</span>
          </div>
          <div className="trust-row">
            <span><ShieldCheck size={16} /> Reserva protegida</span>
            <span><CreditCard size={16} /> Pago sandbox local</span>
          </div>
          {raffle.status === "closed" && (
            <p className="notice">Esta rifa ya esta cerrada. Numero ganador: {raffle.winner_number}</p>
          )}
        </div>
        <div className="prize-frame">
          {raffle.prize_image_url ? (
            <img src={raffle.prize_image_url} alt={`Premio de ${raffle.name}`} />
          ) : (
            <div className="ticket-visual">
              <span>Premio</span>
              <Gift size={42} />
              <strong>{raffle.prize_description}</strong>
              <small>{numberLabel(0, raffle.total_numbers)} - {numberLabel(raffle.total_numbers - 1, raffle.total_numbers)}</small>
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
        <article>
          <span>Estado</span>
          <strong>{raffle.status === "active" ? "Activa" : "Cerrada"}</strong>
        </article>
      </section>

      <div className="public-layout">
        <section className="panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Boletas</p>
              <h2><Ticket size={19} /> Escoge tu numero</h2>
            </div>
            <div className="legend">
              <span><i className="dot available" /> Disponible</span>
              <span><i className="dot reserved" /> Reservado</span>
              <span><i className="dot sold" /> Vendido</span>
            </div>
          </div>

          {raffle.status === "closed" ? (
            <p className="empty-state">La rifa ya fue cerrada por el organizador.</p>
          ) : (
            <div className="number-grid">
              {raffle.numbers.map((item) => (
                <button
                  type="button"
                  key={item.number}
                  className={`number ${item.status} ${selected === item.number ? "selected" : ""}`}
                  disabled={item.status !== "available" || saving}
                  onClick={() => setSelected(item.number)}
                >
                  {numberLabel(item.number, raffle.total_numbers)}
                </button>
              ))}
            </div>
          )}
        </section>

        {raffle.status === "active" && (
          <aside className="panel reservation-panel">
            <p className="eyebrow">Reserva</p>
            <h2><Ticket size={19} /> {selected === null ? "Selecciona un numero" : `Numero ${numberLabel(selected, raffle.total_numbers)}`}</h2>
            <p className="muted">
              Los pagos en efectivo quedan pendientes hasta que el organizador los confirme. Los pagos digitales se
              pueden simular localmente porque Wompi esta en modo sandbox.
            </p>

            <form onSubmit={reserve} className="form">
              <label>
                Nombre completo
                <input required minLength="3" value={buyer.buyer_name} onChange={(e) => setBuyer({ ...buyer, buyer_name: e.target.value })} />
              </label>
              <label>
                Celular WhatsApp
                <input required value={buyer.buyer_phone} placeholder="+573001112233" onChange={(e) => setBuyer({ ...buyer, buyer_phone: e.target.value })} />
              </label>
              <label>
                Email opcional
                <input type="email" value={buyer.buyer_email} onChange={(e) => setBuyer({ ...buyer, buyer_email: e.target.value })} />
              </label>
              <label>
                Metodo de pago
                <select value={buyer.payment_method} onChange={(e) => setBuyer({ ...buyer, payment_method: e.target.value })}>
                  <option value="cash">Efectivo</option>
                  <option value="card">Tarjeta</option>
                  <option value="pse">PSE</option>
                </select>
              </label>
              <button type="submit" disabled={saving || selected === null || selectedState !== "available"}>
                <CheckCircle2 size={17} /> {saving ? "Procesando..." : "Reservar numero"}
              </button>
            </form>

            {checkout?.sandbox && digitalReservation && (
              <div className="sandbox-box">
                <strong>Checkout sandbox</strong>
                <p>Referencia local: {checkout.reference}</p>
                <button type="button" onClick={simulatePayment} disabled={saving}>
                  <CreditCard size={17} /> Simular pago aprobado
                </button>
              </div>
            )}
          </aside>
        )}
      </div>
    </main>
  );
}
