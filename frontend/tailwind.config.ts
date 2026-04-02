import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand backgrounds
        surface: {
          deepest: "#05070D",
          deep: "#0A0F1A",
          base: "#0F1626",
          raised: "#131C31",
        },
        // Accent palette
        accent: {
          blue: "#3B82F6",
          sky: "#38BDF8",
          indigo: "#6366F1",
          violet: "#7C3AED",
        },
        // Text
        text: {
          primary: "#FFFFFF",
          secondary: "#A1AABF",
          muted: "#6F778A",
        },
        // Status
        status: {
          success: "#22C55E",
          warning: "#F59E0B",
          error: "#EF4444",
        },
        // Border
        border: {
          subtle: "rgba(255,255,255,0.08)",
        },
      },
      fontFamily: {
        heading: ["Space Grotesk", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      backgroundImage: {
        "gradient-brand":
          "linear-gradient(135deg, #3B82F6, #38BDF8, #6366F1)",
        "gradient-cta":
          "linear-gradient(135deg, #3B82F6 0%, #6366F1 100%)",
      },
      boxShadow: {
        glow: "0 0 20px rgba(59, 130, 246, 0.3)",
        "glow-lg": "0 0 40px rgba(59, 130, 246, 0.25)",
        "glow-accent": "0 0 24px rgba(99, 102, 241, 0.35)",
      },
      borderRadius: {
        xl: "12px",
        "2xl": "16px",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
