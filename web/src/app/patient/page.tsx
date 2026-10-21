import type { Metadata } from "next";
import { RequireSession } from "@/components/RequireSession";
import { PatientForm } from "@/components/pages/PatientForm";

export const metadata: Metadata = { title: "Person" };

export default function PatientPage() {
  return (
    <RequireSession>
      <PatientForm />
    </RequireSession>
  );
}
