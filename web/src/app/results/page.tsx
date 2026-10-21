import type { Metadata } from "next";
import { RequireSession } from "@/components/RequireSession";
import { ResultsView } from "@/components/pages/ResultsView";

export const metadata: Metadata = { title: "Prices" };

export default function ResultsPage() {
  return (
    <RequireSession>
      <ResultsView />
    </RequireSession>
  );
}
