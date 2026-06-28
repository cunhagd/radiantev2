import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'happy-dom',
    environmentOptions: {
      happyDOM: {
        settings: {
          disableJavaScriptFileLoad: false,
        },
      },
    },
    include: ['tests/**/*.test.js'],
    setupFiles: ['tests/setup.js'],
    server: {
      deps: {
        // inline os modulos JS para que sejam processados pelo Vitest
        inline: [/.*/],
      },
    },
  },
});
