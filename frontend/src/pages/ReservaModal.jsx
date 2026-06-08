import { useState } from "react";
import { PhoneInput } from "react-international-phone";
import "react-international-phone/style.css";
import { AVISO_PAGO, EMPTY_BUYER, LABEL_BOTON_PAGO } from "../lib/constants.js";
import { request } from "../lib/api.js";

export default function ReservaModal({ number, token, onConfirm, onClose, error }) {
  const [buyer, setBuyer] = useState(EMPTY_BUYER);
  const [redirigiendo, setRedirigiendo] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    const payload = { ...buyer, buyer_email: buyer.buyer_email || null, number };
    const reserva = await onConfirm(payload);

    if (reserva && buyer.payment_method !== "cash") {
      setRedirigiendo(true);
      const checkout = await request(`/r/${token}/reservations/${reserva.id}/checkout`, { method: "POST" });
      window.location.href = checkout.checkout_url;
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <h2>Reservar número {String(number).padStart(2, "0")}</h2>
        <form onSubmit={handleSubmit} className="form">
          <div className="field">
            <label>Nombre completo *</label>
            <input
              required
              value={buyer.buyer_name}
              onChange={(e) => setBuyer({ ...buyer, buyer_name: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Celular *</label>
            <PhoneInput
              defaultCountry="co"
              value={buyer.buyer_phone}
              onChange={(phone) => setBuyer({ ...buyer, buyer_phone: phone })}
            />
          </div>
          <div className="field">
            <label>Email (opcional)</label>
            <input
              type="email"
              value={buyer.buyer_email}
              onChange={(e) => setBuyer({ ...buyer, buyer_email: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Método de pago</label>
            <select
              value={buyer.payment_method}
              onChange={(e) => setBuyer({ ...buyer, payment_method: e.target.value })}
            >
              <option value="cash">Efectivo</option>
              <option value="card">Tarjeta</option>
              <option value="pse">PSE</option>
            </select>
          </div>
          <p className="muted">{AVISO_PAGO[buyer.payment_method]}</p>
          {error && <p className="modal-error">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={redirigiendo}>
              Cancelar
            </button>
            <button type="submit" disabled={redirigiendo}>
              {redirigiendo ? "Redirigiendo a Wompi..." : LABEL_BOTON_PAGO[buyer.payment_method]}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
