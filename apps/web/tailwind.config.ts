import type { Config } from "tailwindcss";

/**
 * Datask design tokens — sourced from docs/Design.md
 * Dark-only brand system: black canvas + white ink + single blue accent + gradient cards.
 */
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Surfaces
        canvas: "#0C0C0C",        // near-black with faint warmth — page background
        "surface-1": "#161514",   // one step above canvas: cards, secondary buttons
        "surface-2": "#1F1E1C",   // two steps: featured cards, selected states
        // Text
        ink: "#FFFFFF",           // all headlines, emphasized body
        "ink-muted": "#999999",   // secondary: meta, footer, deselected tabs
        // Borders
        hairline: "rgba(255,255,255,0.10)",
        "hairline-soft": "rgba(255,255,255,0.06)",
        // Accent
        "accent-blue": "#0099FF", // hyperlinks, focus rings, selection — never decorative
        // Semantic
        "success-green": "#22C55E",
      },
      fontFamily: {
        display: [
          "Mona Sans",
          "Geist",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
        body: [
          "Inter Variable",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        // Design token scale
        "display-xxl": ["110px", { lineHeight: "0.85", letterSpacing: "-5.5px", fontWeight: "500" }],
        "display-xl": ["85px", { lineHeight: "0.95", letterSpacing: "-4.25px", fontWeight: "500" }],
        "display-lg": ["62px", { lineHeight: "1.00", letterSpacing: "-3.1px", fontWeight: "500" }],
        "display-md": ["32px", { lineHeight: "1.13", letterSpacing: "-1.0px", fontWeight: "500" }],
        headline: ["22px", { lineHeight: "1.20", letterSpacing: "-0.8px", fontWeight: "700" }],
        subhead: ["24px", { lineHeight: "1.30", letterSpacing: "-0.01px", fontWeight: "400" }],
        "body-lg": ["18px", { lineHeight: "1.30", letterSpacing: "-0.18px" }],
        body: ["15px", { lineHeight: "1.30", letterSpacing: "-0.15px" }],
        "body-sm": ["14px", { lineHeight: "1.40", letterSpacing: "-0.14px", fontWeight: "500" }],
        caption: ["13px", { lineHeight: "1.20", letterSpacing: "-0.13px", fontWeight: "500" }],
        micro: ["12px", { lineHeight: "1.20", letterSpacing: "-0.12px" }],
        btn: ["14px", { lineHeight: "1.0", letterSpacing: "-0.14px", fontWeight: "500" }],
      },
      borderRadius: {
        xs: "4px",
        sm: "6px",
        md: "10px",
        lg: "15px",
        xl: "20px",
        "2xl": "30px",
        pill: "100px",
        full: "9999px",
      },
      spacing: {
        // 5px base unit
        hair: "1px",
        xxs: "4px",
        xs: "8px",
        sm: "12px",
        md: "15px",
        lg: "20px",
        xl: "30px",
        "2xl": "40px",
        section: "96px",
      },
      boxShadow: {
        "elevation-1": "0px 10px 30px rgba(0,0,0,0.25)",
        "elevation-2": "inset 0px 0.5px 0px rgba(255,255,255,0.10), 0px 10px 30px rgba(0,0,0,0.25)",
        "elevation-3": "0 0 0 1px rgba(0,153,255,0.15)",
        focus: "0 0 0 1px #0099FF",
      },
      backgroundImage: {
        // Gradient spotlight card variants
        "gradient-violet": "linear-gradient(135deg, #2D1060 0%, #6B21C8 60%, #9B40E0 100%)",
        "gradient-magenta": "linear-gradient(135deg, #5C0A4A 0%, #C0248C 60%, #E840B0 100%)",
        "gradient-orange": "linear-gradient(135deg, #5C2000 0%, #C84010 60%, #F07030 100%)",
        "gradient-coral": "linear-gradient(135deg, #5C1010 0%, #C83030 60%, #F05858 100%)",
      },
      maxWidth: {
        container: "1199px",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out forwards",
        "fade-in": "fade-in 0.4s ease-out forwards",
      },
    },
  },
  plugins: [],
};

export default config;
