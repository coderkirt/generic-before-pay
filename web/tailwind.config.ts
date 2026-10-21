import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#ffffff",
        ink: "#0b0c0c",
        muted: "#3c4448",
        line: "#b1b4b6",
        link: "#1d4f91",
        focus: "#ffdd00",
      },
    },
  },
  plugins: [],
};

export default config;
