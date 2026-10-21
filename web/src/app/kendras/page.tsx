import type { Metadata } from "next";
import { KendrasView } from "@/components/pages/KendrasView";

export const metadata: Metadata = { title: "Kendras" };

export default function KendrasPage() {
  return <KendrasView />;
}
