import { render } from "@testing-library/react";
import { Providers } from "@/components/Providers";
import type { SessionState } from "@/lib/session/reducer";

export function renderApp(ui: React.ReactNode, initialSession?: SessionState) {
  return render(<Providers initialSession={initialSession}>{ui}</Providers>);
}
