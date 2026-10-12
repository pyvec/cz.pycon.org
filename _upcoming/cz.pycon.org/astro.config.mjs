// @ts-check
import { defineConfig } from "astro/config";
import { browserslistToTargets } from "lightningcss";

// Vite's default browser targets, set for both CSS steps. Astro builds for esnext, which would let
// the minifier turn the lowered min-width queries back into range syntax.
const browsers = ["chrome 87", "edge 88", "firefox 78", "safari 14"];

// https://astro.build/config
export default defineConfig({
  site: "https://cz.pycon.org/2027/",
  base: "/2027/",
  outDir: "../public/2027/",
  vite: {
    // Lightning CSS lowers nesting and range media queries and adds vendor prefixes
    css: {
      transformer: "lightningcss",
      lightningcss: { targets: browserslistToTargets(browsers), drafts: { customMedia: true } },
    },
    build: {
      cssMinify: "lightningcss",
      cssTarget: browsers.map((browser) => browser.replace(" ", "")),
    },
  },
});
