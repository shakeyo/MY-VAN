/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
		'./pages/**/*.{ts,tsx}',
		'./components/**/*.{ts,tsx}',
		'./app/**/*.{ts,tsx}',
		'./src/**/*.{ts,tsx}',
	],
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px',
			},
		},
		extend: {
			colors: {
				// RV Dashboard Theme Colors
				'rv-bg': '#111827',
				'rv-surface': '#1F2937',
				'rv-border': '#374151',
				'rv-primary': '#00A0FF',
				'rv-primary-glow': 'rgba(0, 160, 255, 0.4)',
				'rv-success': '#4ADE80',
				'rv-warning': '#FBBF24',
				'rv-danger': '#EF4444',
				'rv-text': '#F9FAFB',
				'rv-text-muted': '#9CA3AF',
				// Legacy support
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: '#00A0FF',
					foreground: '#F9FAFB',
				},
				secondary: {
					DEFAULT: '#4ADE80',
					foreground: '#F9FAFB',
				},
				accent: {
					DEFAULT: '#FBBF24',
					foreground: '#F9FAFB',
				},
				destructive: {
					DEFAULT: '#EF4444',
					foreground: '#F9FAFB',
				},
				muted: {
					DEFAULT: '#374151',
					foreground: '#9CA3AF',
				},
				popover: {
					DEFAULT: '#1F2937',
					foreground: '#F9FAFB',
				},
				card: {
					DEFAULT: '#1F2937',
					foreground: '#F9FAFB',
				},
			},
			fontFamily: {
				'sans': ['Inter', 'system-ui', 'sans-serif'],
				'mono': ['JetBrains Mono', 'Roboto Mono', 'monospace'],
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
			},
			keyframes: {
				'accordion-down': {
					from: { height: 0 },
					to: { height: 'var(--radix-accordion-content-height)' },
				},
				'accordion-up': {
					from: { height: 'var(--radix-accordion-content-height)' },
					to: { height: 0 },
				},
				'pulse-glow': {
					'0%, 100%': { boxShadow: '0 0 10px rgba(0, 160, 255, 0.4)' },
					'50%': { boxShadow: '0 0 20px rgba(0, 160, 255, 0.6)' },
				},
				'wave': {
					'0%': { transform: 'translateX(-100%)' },
					'100%': { transform: 'translateX(100%)' },
				},
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
			},
		},
	},
	plugins: [require('tailwindcss-animate')],
}
