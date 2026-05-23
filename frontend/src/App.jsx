import React from "react";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import PublicRaffle from "./pages/PublicRaffle.jsx";

function PaymentResult() {
  const params = new URLSearchParams(window.location.search);
  const status = params.get("status") ?? "pending";
  const reference = params.get("reference");
  const ok = ["APPROVED", "paid", "success"].includes(status);

  return (
    <main className="app-shell">
      <section className="panel">
        <p className="eyebrow">Pago Wompi</p>
        <h1>{ok ? "Pago recibido" : "Pago en validacion"}</h1>
        <p className="muted">
          {ok
            ? "Tu boleta quedara marcada como vendida cuando Wompi confirme el webhook."
            : "Si el pago fue rechazado, puedes volver a la rifa e intentar con otro metodo."}
        </p>
        {reference && <code>Referencia: {reference}</code>}
      </section>
    </main>
  );
}

export default function App() {
  const path = window.location.pathname;

  if (path.startsWith("/payment-result")) {
    return <PaymentResult />;
  }

  if (path.startsWith("/r/")) {
    return <PublicRaffle token={path.split("/").filter(Boolean)[1]} />;
  }

  return <AdminDashboard />;
}
