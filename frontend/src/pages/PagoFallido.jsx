export default function PagoFallido() {
  function reintentar() {
    window.history.back();
  }

  return (
    <main className="shell">
      <section className="panel" style={{ textAlign: "center", padding: "48px 24px" }}>
        <h1>Pago no completado</h1>
        <p>El pago fue rechazado o cancelado. Tu número ha sido liberado.</p>
        <p className="muted">Puedes intentarlo de nuevo seleccionando el número en la rifa.</p>
        <button onClick={reintentar} style={{ marginTop: "20px" }}>
          Volver e intentar de nuevo
        </button>
      </section>
    </main>
  );
}
