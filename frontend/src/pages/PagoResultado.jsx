export default function PagoResultado() {
  const params = new URLSearchParams(window.location.search);
  const transaccionId = params.get("id");

  return (
    <main className="shell">
      <section className="panel" style={{ textAlign: "center", padding: "48px 24px" }}>
        <h1>Pago en proceso</h1>
        <p>Tu pago está siendo procesado por Wompi.</p>
        <p>
          Una vez confirmado, tu número quedará marcado como <strong>vendido</strong> y
          recibirás la confirmación.
        </p>
        {transaccionId && (
          <p className="muted">Referencia de transacción: <code>{transaccionId}</code></p>
        )}
        <p className="muted">Puedes cerrar esta ventana con seguridad.</p>
      </section>
    </main>
  );
}
