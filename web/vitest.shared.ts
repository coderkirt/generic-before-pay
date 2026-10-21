import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const root = import.meta.dirname;

export function vitestConfig(include: string[]) {
  return defineConfig({
    plugins: [react()],
    resolve: {
      alias: { "@": path.resolve(root, "src") },
    },
    test: {
      environment: "jsdom",
      setupFiles: ["./vitest.setup.ts"],
      include,
    },
  });
}
