import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  base: process.env.BASE_PATH ?? '/',
  resolve: { tsconfigPaths: true },
  plugins: [
    tanstackStart({
      prerender: {
        enabled: true,
      },
    }),
    viteReact(),
  ],
})
