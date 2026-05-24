import AdminDashboard from "./pages/AdminDashboard.jsx";
import PagoExitoso from "./pages/PagoExitoso.jsx";
import PagoFallido from "./pages/PagoFallido.jsx";
import PagoResultado from "./pages/PagoResultado.jsx";
import PublicRaffle from "./pages/PublicRaffle.jsx";

export default function App() {
  const path = window.location.pathname;

  if (path.startsWith("/r/")) {
    return <PublicRaffle token={path.split("/").filter(Boolean)[1]} />;
  }
  if (path === "/pago/resultado") return <PagoResultado />;
  if (path === "/pago/exitoso") return <PagoExitoso />;
  if (path === "/pago/fallido") return <PagoFallido />;

  return <AdminDashboard />;
}
