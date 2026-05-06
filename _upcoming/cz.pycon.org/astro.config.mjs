// @ts-check
import { defineConfig } from "astro/config";

import purgecss from "astro-purgecss";

// https://astro.build/config
export default defineConfig({
  site: "https://cz.pycon.org/2027/",
  base: "/2027/",
  outDir: "../public/2027/",
  integrations: [purgecss()],
});
