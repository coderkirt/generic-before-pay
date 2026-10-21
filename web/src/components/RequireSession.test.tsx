import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequireSession } from "@/components/RequireSession";
import { RECOVERY_MESSAGE } from "@/lib/copy/approved";
import { initialSession, sessionReducer } from "@/lib/session/reducer";
import { renderApp } from "@/test/render";

describe("RequireSession", () => {
  it("shows the recovery screen instead of a blank page when the session is empty", () => {
    renderApp(
      <RequireSession>
        <p>confirmed medicine</p>
      </RequireSession>,
    );
    expect(screen.getByRole("heading", { level: 1, name: RECOVERY_MESSAGE })).toBeInTheDocument();
    expect(screen.queryByText("confirmed medicine")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Start again" })).toHaveAttribute("href", "/");
  });

  it("renders the step once the session has started", () => {
    renderApp(
      <RequireSession>
        <h1>Check names</h1>
      </RequireSession>,
      sessionReducer(initialSession, { type: "start" }),
    );
    expect(screen.getByRole("heading", { name: "Check names" })).toBeInTheDocument();
    expect(screen.queryByText(RECOVERY_MESSAGE)).not.toBeInTheDocument();
  });
});
