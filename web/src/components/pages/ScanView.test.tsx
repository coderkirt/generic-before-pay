import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ScanView } from "@/components/pages/ScanView";
import { OcrClientError, type OcrProvider } from "@/lib/ocr/types";
import { renderApp } from "@/test/render";

const push = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  usePathname: () => "/scan",
  useRouter: () => ({ push }),
}));

const failing: OcrProvider = {
  async readText() {
    throw new OcrClientError("RATE_LIMITED", 3);
  },
};

describe("scan errors", () => {
  it("shows a rate-limit message and a way to type names", async () => {
    const user = userEvent.setup();
    renderApp(<ScanView provider={failing} />);
    const file = new File([new Uint8Array([1, 2, 3])], "slip.jpg", { type: "image/jpeg" });
    const input = document.querySelector("input[type=file]");
    if (!(input instanceof HTMLInputElement)) throw new Error("missing file input");
    await user.upload(input, file);
    expect(await screen.findByRole("alert")).toHaveTextContent("Too many scans");
    expect(screen.getByText(/Suggested wait, in seconds:/)).toHaveTextContent("3");
    expect(screen.getByRole("button", { name: "Type medicine names instead" })).toBeEnabled();
  });
});
