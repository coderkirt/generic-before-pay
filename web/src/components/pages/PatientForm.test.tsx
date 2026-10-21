import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PatientForm, ageError } from "@/components/pages/PatientForm";
import { initialSession, sessionReducer } from "@/lib/session/reducer";
import { renderApp } from "@/test/render";

const push = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  usePathname: () => "/patient",
  useRouter: () => ({ push }),
}));

describe("patient confirmation", () => {
  it("rejects a missing age and asks before continuing", async () => {
    const user = userEvent.setup();
    expect(ageError("")).toBe(true);
    expect(ageError("121")).toBe(true);
    expect(ageError("34")).toBe(false);
    renderApp(<PatientForm />, sessionReducer(initialSession, { type: "start" }));
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.getByText("Enter an age from 0 to 120 years.")).toBeInTheDocument();
    await user.type(screen.getByLabelText("Age in years"), "34");
    await user.click(screen.getByRole("radio", { name: "Female" }));
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.getByText(/34-/)).toHaveTextContent("Is this prescription for a 34-year-old Female?");
    await user.click(screen.getByRole("button", { name: "Edit" }));
    expect(screen.getByLabelText("Age in years")).toBeInTheDocument();
  });
});
