// @ts-check
import { defineConfig } from "astro/config";

import purgecss from "astro-purgecss";

// https://astro.build/config
export default defineConfig({
  site: "https://cz.pycon.org/2026/",
  base: "/2026/",
  outDir: "../public/2026/",
  integrations: [purgecss()],
});
