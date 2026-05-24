export const AVISO_PAGO = {
  cash: "Tendrás 5 días hábiles para entregar el efectivo y confirmar tu boleta.",
  card: "Serás redirigido a Wompi para completar el pago con tarjeta ahora mismo.",
  pse: "Serás redirigido a Wompi para completar el pago por PSE ahora mismo.",
};

export const LABEL_BOTON_PAGO = {
  cash: "Reservar número",
  card: "Ir a pagar con tarjeta →",
  pse: "Ir a pagar por PSE →",
};

export const EMPTY_BUYER = {
  buyer_name: "",
  buyer_phone: "",
  buyer_email: "",
  payment_method: "cash",
};

export const NOMBRES_CAMPO = {
  total_numbers: "Cantidad de números",
  ticket_price: "Valor por boleta",
  name: "Nombre",
  prize_description: "Descripción del premio",
  draw_date: "Fecha del sorteo",
  lottery_type: "Tipo de lotería",
  prize_image_url: "URL imagen del premio",
  password: "Contraseña",
  email: "Email",
  full_name: "Nombre completo",
  buyer_name: "Nombre del comprador",
  buyer_phone: "Celular",
  buyer_email: "Email del comprador",
  number: "Número",
};

export const MENSAJES_VALIDACION = {
  string_too_short: (ctx) => `Debe tener al menos ${ctx?.min_length} caracteres`,
  string_too_long: (ctx) => `No puede tener más de ${ctx?.max_length} caracteres`,
  greater_than_equal: (ctx) => `Debe ser mayor o igual a ${ctx?.ge}`,
  less_than_equal: (ctx) => `Debe ser menor o igual a ${ctx?.le}`,
  greater_than: (ctx) => `Debe ser mayor que ${ctx?.gt}`,
  less_than: (ctx) => `Debe ser menor que ${ctx?.lt}`,
  missing: () => "Campo requerido",
  value_error: () => "Valor inválido",
  string_pattern_mismatch: () => "Formato inválido",
};
