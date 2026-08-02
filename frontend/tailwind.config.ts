import type { Config } from 'tailwindcss'

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Roboto Flex', 'system-ui', 'sans-serif'],
        mono: ['Berkeley Mono', 'SFMono-Regular', 'ui-monospace', 'monospace'],
        display: ['Crimson Text', 'serif'],
        brand: ['Yusei Magic', 'system-ui', 'sans-serif'],
      },
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        muted: 'hsl(var(--muted))',
        border: 'hsl(var(--border))',
        card: 'hsl(var(--card))',
        signal: {
          bear: '#FF5D00',
          base: '#FF5D00',
          bull: '#FF5D00',
          missing: '#111111',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
