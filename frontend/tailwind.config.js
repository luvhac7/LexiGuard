/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        lg: '2rem',
        xl: '2rem',
        '2xl': '2rem',
      },
    },
    extend: {
      colors: {
        brand: {
          DEFAULT: 'var(--primary)',
          foreground: '#ffffff',
        },
        accent: 'var(--accent)',
        background: 'var(--background)',
        primary: 'var(--primary)',
        'primary-light': 'var(--primary-light)',
        surface: 'var(--surface)',
        'surface-light': 'var(--surface-light)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-muted': 'var(--text-muted)',
      },
      boxShadow: {
        brand: '0 10px 20px rgba(30, 42, 120, 0.15)',
      },
      borderRadius: {
        'xl': '14px',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.98)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out both',
        'slide-up': 'slide-up 0.6s ease-out both',
        'scale-in': 'scale-in 0.25s ease-out both',
        'shimmer': 'shimmer 2s linear infinite',
      },
    },
  },
  plugins: [],
}
