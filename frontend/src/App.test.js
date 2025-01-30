import { render, screen } from "@testing-library/react";
import App from "./App";

test("title: SSSS", () => {
  render(<App />);
  const linkElement = screen.getByText(/Super Secret Santa Selector/i);
  expect(linkElement).toBeInTheDocument();
});
