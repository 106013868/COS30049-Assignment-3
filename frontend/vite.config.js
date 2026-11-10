import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // the back end's address, so the Content Security Policy allows calls to it
  const api = loadEnv(mode, process.cwd()).VITE_API_BASE_URL

  // Security headers on every page of the built app
  const securityHeaders = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
    'Content-Security-Policy': [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self' https://fonts.googleapis.com",
      "font-src https://fonts.gstatic.com",
      `connect-src 'self' ${api}`,
      "img-src 'self' data:",
      "object-src 'none'",
      "base-uri 'none'",
      "form-action 'none'",
      "frame-ancestors 'none'",
    ].join('; '),
  }

  return {
    plugins: [react()],
    // npm run preview serves the built app on 5173
    preview: { port: 5173, strictPort: true, headers: securityHeaders },
  }
})
