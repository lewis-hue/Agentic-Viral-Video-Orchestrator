/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        poppins: ['Poppins', 'sans-serif'],
        roboto: ['Roboto', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.9375rem', { lineHeight: '1.375rem' }],
        'sm': ['1.0625rem', { lineHeight: '1.625rem' }],
        'base': ['1.1875rem', { lineHeight: '1.875rem' }],
        'lg': ['1.3125rem', { lineHeight: '1.875rem' }],
        'xl': ['1.5625rem', { lineHeight: '2.125rem' }],
        '2xl': ['1.9375rem', { lineHeight: '2.375rem' }],
        '3xl': ['2.3125rem', { lineHeight: '2.625rem' }],
        '4xl': ['3.125rem', { lineHeight: '1.125' }],
        '5xl': ['3.875rem', { lineHeight: '1.125' }],
        '6xl': ['4.625rem', { lineHeight: '1.125' }],
      },
      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',
        medium: '450',
        semibold: '550',
        bold: '650',
        extrabold: '750',
        black: '850',
      },
      colors: {
        primary: '#0075FF',
        accent: '#0075FF',
        secondary: '#F7F8FA',
        background: '#FFFFFF',
        card: '#FFFFFF',
        text: {
          DEFAULT: '#1E293B',
          light: '#64748B',
        },
        border: 'rgba(100, 116, 139, 0.2)',
        success: 'rgba(0, 117, 255, 0.1)',
        error: '#DC3545',
        yellow: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
      },
      borderRadius: {
        'xl': '12px',
      },
      boxShadow: {
        'custom': '0 4px 12px rgba(0, 0, 0, 0.08)',
        'custom-hover': '0 8px 24px rgba(0, 0, 0, 0.12)',
      }
    }
  },
  plugins: [],
}