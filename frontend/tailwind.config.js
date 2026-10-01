/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          abyss: 'var(--bg-abyss)',
          panel: 'var(--bg-panel)',
        },
        border: {
          glass: 'var(--border-glass)',
        },
        text: {
          primary: 'var(--text-primary)',
          muted: 'var(--text-muted)',
        },
        accent: 'var(--accent)',
        risk: {
          critical: 'var(--risk-critical)',
          high: 'var(--risk-high)',
          suspicious: 'var(--risk-suspicious)',
          clean: 'var(--risk-clean)',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
