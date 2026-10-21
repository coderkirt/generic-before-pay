import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach } from "vitest";

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
});
