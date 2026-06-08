import { useEffect, useMemo, useState } from "react";
import { request } from "../lib/api.js";
import ReservaModal from "./ReservaModal.jsx";

function formatMoney(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function PublicRaffle({ token }) {
  const [raffle, setRaffle] = useState(null);
  const [selected, setSelected] = useState(null);
  const [modalError, setModalError] = useState("");
  const [notice, setNotice] = useState("");

  const counts = useMemo(() => {
    if (!raffle) return { available: 0, reserved: 0, sold: 0 };
    return raffle.numbers.reduce(
      (acc, item) => ({ ...acc, [item.status]: (acc[item.status] || 0) + 1 }),
      { available: 0, reserved: 0, sold: 0 },
    );
  }, [raffle]);

  async function loadRaffle() {
    const data = await request(`/r/${token}`);
    setRaffle(data);
  }

  useEffect(() => {
    loadRaffle().catch((err) => setNotice(err.message));
  }, [token]);

  async function handleConfirm(payload) {
    setModalError("");
    try {
      const reserva = await request(`/r/${token}/reserve`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (payload.payment_method === "cash") {
        setSelected(null);
        setNotice("¡Número reservado! Tienes 5 días para completar el pago en efectivo.");
        await loadRaffle();
      }
      return reserva;
    } catch (err) {
      if (err.status === 409) {
        setModalError("Este número acaba de ser tomado. Elige otro.");
        await loadRaffle();
      } else {
        setModalError(err.message);
      }
      return null;
    }
  }

  if (!raffle) {
    return <main className="shell">{notice || "Cargando rifa..."}</main>;
  }

  const isClosed = raffle.status === "closed";
  const selectedState = raffle.numbers.find((n) => n.number === selected)?.status;
  const showModal = selected !== null && selectedState === "available" && !isClosed;

  return (
    <main className="shell">
      {isClosed && (
        <p className="notice notice-closed">
          Esta rifa está cerrada. Ya no se aceptan reservas.
        </p>
      )}

      <section className="public-hero">
        <div>
          <p className="eyebrow">{raffle.lottery_type}</p>
          <h1>{raffle.name}</h1>
          <p>{raffle.prize_description}</p>
          <strong>{formatMoney(raffle.ticket_price)} por boleta</strong>
          <p className="muted">Sorteo: {new Date(raffle.draw_date).toLocaleString("es-CO")}</p>
        </div>
        {raffle.prize_image_url ? (
          <img src={raffle.prize_image_url} alt={`Premio de ${raffle.name}`} />
        ) : (
          <div className="prize-placeholder">
            <strong>Premio</strong>
            <span>{raffle.prize_description}</span>
          </div>
        )}
      </section>

      {notice && <p className="notice">{notice}</p>}

      {isClosed && (
        <p className="notice" style={{ background: "#fef3cd", border: "1px solid #ffe48a", color: "#664d03" }}>
          Esta rifa esta cerrada. Ya no se aceptan reservas ni pagos.
        </p>
      )}

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

      <section className="panel">
        <div className="section-head">
          <h2>Selecciona tu número</h2>
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
              disabled={item.status !== "available" || isClosed}
              onClick={() => { setNotice(""); setSelected(item.number); }}
            >
              {item.number.toString().padStart(2, "0")}
            </button>
          ))}
        </div>
      </section>

      {showModal && (
        <ReservaModal
          number={selected}
          token={token}
          onConfirm={handleConfirm}
          onClose={() => { setSelected(null); setModalError(""); }}
          error={modalError}
        />
      )}
    </main>
  );
}
