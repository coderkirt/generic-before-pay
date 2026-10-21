import type { Metadata } from "next";
import { ScanView } from "@/components/pages/ScanView";

export const metadata: Metadata = { title: "Scan" };

export default function ScanPage() {
  return <ScanView />;
}
