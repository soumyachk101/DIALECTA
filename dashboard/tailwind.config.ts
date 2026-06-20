import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { base: "#0A0A0C", elevated: "#13141A" },
        border: { subtle: "#23252E" },
        text: { primary: "#F4F4F6", muted: "#8B8D98" },
        accent: {
          cyan: "#38BDF8",
          violet: "#7C3AED",
          amber: "#F5A524",
          emerald: "#34D399",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
        sans: ["Space Grotesk", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};
export default config;
