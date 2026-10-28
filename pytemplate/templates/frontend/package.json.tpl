{
  "name": "{{PROJECT_NAME}}-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite --port {{FRONTEND_DEV_PORT}} --strictPort",
    "build": "vue-tsc --noEmit && vite build",
    "build:external": "vue-tsc --noEmit && vite build --mode external",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.31"{{ELEMENT_PLUS_DEP}}
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.5",
    "typescript": "^5.5.3",
    "vite": "^5.3.4",
    "vue-tsc": "^2.0.26"
  }
}
