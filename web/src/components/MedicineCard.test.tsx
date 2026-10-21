import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { DidYouMean } from "@/components/DidYouMean";
import { MedicineCard } from "@/components/MedicineCard";
import { SavingCard } from "@/components/SavingCard";
import { loadBundledCatalog } from "@/lib/data/load";
import { priceLine } from "@/lib/pricing/selection";
import { buildLine } from "@/lib/session/lines";
import { renderApp } from "@/test/render";

describe("price display", () => {
  it("shows no rupee amount for an uncertain medicine", () => {
    const catalog = loadBundledCatalog();
    if (!catalog.ok) throw new Error("catalog");
    const line = buildLine("Crosin", catalog.records, "crosin");
    renderApp(<MedicineCard line={line} record={undefined} priced={priceLine(line, undefined)} />);
    expect(screen.getByText("Not certain")).toBeInTheDocument();
    expect(screen.queryByText(/₹/)).not.toBeInTheDocument();
    expect(screen.getAllByText("No price until this name is confirmed.").length).toBeGreaterThan(0);
  });

  it("offers dataset names without prices", async () => {
    const user = userEvent.setup();
    const catalog = loadBundledCatalog();
    if (!catalog.ok) throw new Error("catalog");
    const line = buildLine("Crosin", catalog.records, "crosin");
    let picked = "";
    renderApp(
      <DidYouMean
        reason={line.reason}
        candidateIds={line.candidateIds}
        records={catalog.records}
        onPick={(id) => {
          picked = id;
        }}
      />,
    );
    expect(screen.queryByText(/₹/)).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Calpol 500/ }));
    expect(picked).toBe("paracetamol-500mg-tab");
  });

  it("renders a listed comparison only from totals", () => {
    renderApp(
      <SavingCard
        totals={{
          brandTotal: 32.5,
          genericTotal: 5,
          listedDifference: 27.5,
          label: "listed saving",
          countedLines: 1,
        }}
      />,
    );
    expect(screen.getAllByText("₹32.50").length).toBeGreaterThan(0);
    expect(screen.getAllByText("₹5").length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "Listed saving" })).toBeInTheDocument();
  });
});
