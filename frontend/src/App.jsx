import AdminDashboard from "./pages/AdminDashboard.jsx";
import PublicRaffle from "./pages/PublicRaffle.jsx";

export default function App() {
  const path = window.location.pathname;

  if (path.startsWith("/r/")) {
    return <PublicRaffle token={path.split("/").filter(Boolean)[1]} />;
  }

  return <AdminDashboard />;
}
