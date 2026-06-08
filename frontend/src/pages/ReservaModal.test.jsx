import { render, screen } from "@testing-library/react";
import ReservaModal from "./ReservaModal";

const mockOnConfirm = jest.fn();
const mockOnClose = jest.fn();

describe("ReservaModal", () => {
  test("muestra instrucciones para pago en efectivo", () => {
    render(
      <ReservaModal
        number={1}
        token="test-token"
        onConfirm={mockOnConfirm}
        onClose={mockOnClose}
      />,
    );

    const instructions = screen.getByText(
      /Contacta al organizador para coordinar el pago\. Tienes 5 d.as\./i,
    );
    expect(instructions).toBeInTheDocument();
  });

  test("muestra el selector de metodo de pago", () => {
    render(
      <ReservaModal
        number={1}
        token="test-token"
        onConfirm={mockOnConfirm}
        onClose={mockOnClose}
      />,
    );

    expect(screen.getByLabelText(/M.todo de pago/i)).toBeInTheDocument();
  });
});
