import { useState, useEffect } from "react";
import { request, API_URL } from "../lib/api.js";

// ===== ISSUE #004: Vista Pública de Rifa =====
export function PublicRaffleView({ publicToken }) {
  const [raffle, setRaffle] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRaffle = async () => {
      try {
        const data = await request(`/r/${publicToken}`);
        setRaffle(data);
      } catch (error) {
        console.error("Error loading raffle:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRaffle();
  }, [publicToken]);

  if (loading) return <div>Cargando rifa...</div>;
  if (!raffle) return <div>Rifa no encontrada</div>;

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl md:text-4xl font-bold mb-4">{raffle.name}</h1>
        
        {raffle.prize_image_url && (
          <img 
            src={raffle.prize_image_url} 
            alt={raffle.name}
            className="w-full h-64 object-cover rounded-lg mb-6"
          />
        )}
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded">
            <div className="text-sm text-gray-600">Tipo de Lotería</div>
            <div className="text-lg font-bold">{raffle.lottery_type}</div>
          </div>
          <div className="bg-green-50 p-4 rounded">
            <div className="text-sm text-gray-600">Valor Boleta</div>
            <div className="text-lg font-bold">${raffle.ticket_price.toLocaleString()}</div>
          </div>
          <div className="bg-purple-50 p-4 rounded">
            <div className="text-sm text-gray-600">Total Números</div>
            <div className="text-lg font-bold">{raffle.total_numbers}</div>
          </div>
          <div className="bg-orange-50 p-4 rounded">
            <div className="text-sm text-gray-600">Fecha Sorteo</div>
            <div className="text-lg font-bold">{new Date(raffle.draw_date).toLocaleDateString()}</div>
          </div>
        </div>
        
        <div className="border-t pt-6">
          <h2 className="text-2xl font-bold mb-4">Premio</h2>
          <p className="text-gray-700 text-lg">{raffle.prize_description}</p>
        </div>
        
        {raffle.status === "closed" && (
          <div className="mt-6 p-4 bg-red-100 border border-red-400 rounded text-red-700">
            <strong>Rifa Cerrada</strong> - Esta rifa ya finalizó su sorteo.
          </div>
        )}
      </div>
    </div>
  );
}

// ===== ISSUE #005: Grilla de Números =====
export function NumberGrid({ publicToken }) {
  const [numbers, setNumbers] = useState([]);
  const [selectedNumber, setSelectedNumber] = useState(null);

  useEffect(() => {
    const fetchNumbers = async () => {
      try {
        const data = await request(`/r/${publicToken}/numbers`);
        setNumbers(data);
      } catch (error) {
        console.error("Error loading numbers:", error);
      }
    };
    fetchNumbers();
  }, [publicToken]);

  const getNumberColor = (state) => {
    const colors = {
      available: "bg-green-500 hover:bg-green-600 cursor-pointer",
      reserved: "bg-yellow-500 cursor-not-allowed",
      sold: "bg-red-500 cursor-not-allowed",
    };
    return colors[state] || "bg-gray-500";
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-6">Selecciona tu Número</h2>
      
      <div className="grid grid-cols-5 md:grid-cols-10 gap-2">
        {numbers.map((num) => (
          <button
            key={num.number}
            onClick={() => num.state === "available" && setSelectedNumber(num.number)}
            disabled={num.state !== "available"}
            className={`
              aspect-square flex items-center justify-center font-bold text-white rounded
              transition-all transform hover:scale-110
              ${getNumberColor(num.state)}
              ${num.state === "available" ? "active:scale-95" : "opacity-75"}
            `}
          >
            {num.number}
          </button>
        ))}
      </div>
      
      {selectedNumber && (
        <div className="mt-8 p-4 bg-blue-100 border border-blue-400 rounded">
          Número {selectedNumber} seleccionado. Haz clic en "Reservar" para continuar.
        </div>
      )}
    </div>
  );
}

// ===== ISSUE #006: Modal de Reserva =====
export function ReservationModal({ publicToken, number, onClose }) {
  const [formData, setFormData] = useState({
    buyer_name: "",
    buyer_phone: "+57",
    buyer_email: "",
    payment_method: "credit_card",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validar teléfono
      if (!formData.buyer_phone.match(/^\+\d{10,}$/)) {
        alert("Teléfono inválido. Incluye código de país (+57...)");
        return;
      }

      const reservation = await request(`/r/${publicToken}/reserve`, "POST", {
        number,
        ...formData,
      });

      if (formData.payment_method === "credit_card") {
        // Redirigir a Wompi
        const checkout = await request(
          `/public/reservations/${reservation.id}/checkout`,
          "POST"
        );
        window.location.href = checkout.checkout_url;
      } else {
        // Pago en efectivo
        alert(`Reserva exitosa. Tienes ${5} días para pagar.`);
        onClose();
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h2 className="text-2xl font-bold mb-4">Reservar Número {number}</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">Nombre Completo *</label>
            <input
              type="text"
              required
              value={formData.buyer_name}
              onChange={(e) => setFormData({...formData, buyer_name: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium">Celular *</label>
            <input
              type="tel"
              required
              placeholder="+573001234567"
              value={formData.buyer_phone}
              onChange={(e) => setFormData({...formData, buyer_phone: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium">Email (opcional)</label>
            <input
              type="email"
              value={formData.buyer_email}
              onChange={(e) => setFormData({...formData, buyer_email: e.target.value})}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium">Método de Pago *</label>
            <select
              value={formData.payment_method}
              onChange={(e) => setFormData({...formData, payment_method: e.target.value})}
              className="w-full border rounded px-3 py-2"
            >
              <option value="credit_card">Tarjeta/PSE (Wompi)</option>
              <option value="cash">Efectivo</option>
            </select>
          </div>

          {formData.payment_method === "cash" && (
            <div className="bg-blue-50 p-3 rounded text-sm text-blue-700">
              Tienes <strong>5 días</strong> para completar el pago. Contacta al organizador.
            </div>
          )}

          {formData.payment_method === "credit_card" && (
            <div className="bg-green-50 p-3 rounded text-sm text-green-700">
              Tienes <strong>48 horas</strong> para completar el pago.
            </div>
          )}

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Procesando..." : "Reservar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ===== ISSUE #008: Panel de Pagos en Efectivo (Admin) =====
export function AdminPaymentPanel({ raffles, token }) {
  const [buyers, setBuyers] = useState([]);
  const [selectedRaffle, setSelectedRaffle] = useState(raffles[0]?.id);
  const [filter, setFilter] = useState("pending");

  useEffect(() => {
    const fetchBuyers = async () => {
      if (!selectedRaffle) return;
      try {
        const data = await request(
          `/raffles/${selectedRaffle}/buyers?status=${filter}`,
          "GET",
          undefined,
          token
        );
        setBuyers(data);
      } catch (error) {
        console.error("Error loading buyers:", error);
      }
    };
    fetchBuyers();
  }, [selectedRaffle, filter, token]);

  const confirmPayment = async (reservationId) => {
    try {
      await request(
        `/raffles/${selectedRaffle}/reservations/${reservationId}/confirm-cash`,
        "PATCH",
        {},
        token
      );
      alert("Pago confirmado");
      // Recargar lista
      setBuyers(buyers.map(b => b.id === reservationId ? {...b, status: "paid"} : b));
    } catch (error) {
      alert("Error al confirmar pago");
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-6">Gestión de Pagos</h2>
      
      <div className="flex gap-4 mb-6">
        <select
          value={selectedRaffle}
          onChange={(e) => setSelectedRaffle(e.target.value)}
          className="border rounded px-3 py-2"
        >
          {raffles.map((r) => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">Todos</option>
          <option value="pending">Pendientes</option>
          <option value="paid">Pagados</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2 text-left">Nombre</th>
              <th className="border p-2 text-left">Celular</th>
              <th className="border p-2 text-left">Número</th>
              <th className="border p-2 text-left">Método</th>
              <th className="border p-2 text-left">Estado</th>
              <th className="border p-2 text-left">Acción</th>
            </tr>
          </thead>
          <tbody>
            {buyers.map((buyer) => (
              <tr key={buyer.id} className="hover:bg-gray-50">
                <td className="border p-2">{buyer.name}</td>
                <td className="border p-2">{buyer.phone}</td>
                <td className="border p-2 font-bold">{buyer.number}</td>
                <td className="border p-2">{buyer.payment_method === "cash" ? "Efectivo" : "Digital"}</td>
                <td className="border p-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    buyer.status === "paid" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                  }`}>
                    {buyer.status}
                  </span>
                </td>
                <td className="border p-2">
                  {buyer.status === "pending" && buyer.payment_method === "cash" && (
                    <button
                      onClick={() => confirmPayment(buyer.id)}
                      className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                    >
                      Confirmar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ===== ISSUE #010: Subida de Imagen =====
export function ImageUpload({ raffleId, onImageUploaded, token }) {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validaciones
    if (file.size > 5 * 1024 * 1024) {
      alert("Imagen muy grande (máx 5MB)");
      return;
    }

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      alert("Formato no soportado (JPG, PNG, WebP)");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/raffles/${raffleId}/image`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();
      if (data.prize_image_url) {
        onImageUploaded(data.prize_image_url);
        alert("Imagen subida exitosamente");
      }
    } catch (error) {
      alert("Error al subir imagen");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium mb-2">Imagen del Premio</label>
      <input
        type="file"
        accept="image/*"
        onChange={handleUpload}
        disabled={uploading}
        className="block w-full border rounded px-3 py-2"
      />
      {uploading && <p className="text-sm text-gray-500 mt-2">Subiendo...</p>}
    </div>
  );
}

// ===== ISSUE #014: Dashboard de Estadísticas =====
export function RaffleStatsView({ raffleId, token }) {
  const [stats, setStats] = useState(null);
  const [buyers, setBuyers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsData = await request(
          `/raffles/${raffleId}/stats`,
          "GET",
          undefined,
          token
        );
        const buyersData = await request(
          `/raffles/${raffleId}/buyers`,
          "GET",
          undefined,
          token
        );
        setStats(statsData);
        setBuyers(buyersData);
      } catch (error) {
        console.error("Error loading stats:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [raffleId, token]);

  if (loading || !stats) return <div>Cargando estadísticas...</div>;

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-6">Estadísticas de la Rifa</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded border border-blue-200">
          <div className="text-sm text-gray-600">Total Recaudado</div>
          <div className="text-2xl font-bold text-blue-600">
            ${stats.total_raised.toLocaleString()}
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded border border-green-200">
          <div className="text-sm text-gray-600">Números Vendidos</div>
          <div className="text-2xl font-bold text-green-600">
            {stats.numbers_sold} ({stats.percentage_sold.toFixed(1)}%)
          </div>
        </div>
        <div className="bg-yellow-50 p-4 rounded border border-yellow-200">
          <div className="text-sm text-gray-600">Reservados</div>
          <div className="text-2xl font-bold text-yellow-600">{stats.numbers_reserved}</div>
        </div>
        <div className="bg-purple-50 p-4 rounded border border-purple-200">
          <div className="text-sm text-gray-600">Disponibles</div>
          <div className="text-2xl font-bold text-purple-600">{stats.numbers_available}</div>
        </div>
      </div>

      <h3 className="text-xl font-bold mb-4">Listado de Compradores</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2 text-left">Nombre</th>
              <th className="border p-2 text-left">Celular</th>
              <th className="border p-2 text-left">Email</th>
              <th className="border p-2 text-center">Número</th>
              <th className="border p-2 text-left">Método Pago</th>
              <th className="border p-2 text-left">Estado</th>
            </tr>
          </thead>
          <tbody>
            {buyers.map((buyer) => (
              <tr key={`${buyer.name}-${buyer.number}`} className="hover:bg-gray-50">
                <td className="border p-2">{buyer.name}</td>
                <td className="border p-2">{buyer.phone}</td>
                <td className="border p-2 text-sm">{buyer.email || "-"}</td>
                <td className="border p-2 text-center font-bold">{buyer.number}</td>
                <td className="border p-2 text-sm">{buyer.payment_method}</td>
                <td className="border p-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    buyer.status === "paid" 
                      ? "bg-green-100 text-green-800" 
                      : buyer.status === "pending"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-gray-100 text-gray-800"
                  }`}>
                    {buyer.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
