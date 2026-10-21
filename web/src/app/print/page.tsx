import type { Metadata } from "next";
import { RequireSession } from "@/components/RequireSession";
import { PrintSheet } from "@/components/pages/PrintSheet";

export const metadata: Metadata = { title: "Print" };

export default function PrintPage() {
  return (
    <RequireSession>
      <PrintSheet />
    </RequireSession>
  );
}
