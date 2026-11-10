# Provisional PyCon CZ 2027 website

The provisional website for PyCon CZ 2027 uses [Astro](https://astro.build) to build a static site for the event.
The Astro project is located in the `cz.pycon.org` subdirectory, the static site is built into the `public` subdirectory.

The site is built automatically by the deployment workflows (`.github/workflows/deploy_*.yaml`), so the `public`
subdirectory is not committed to the repository. Optimized images are cached between builds.

## Development

Requirements to build the site:

* Node.js v18, v20, v22, or v24.

### Installing dependencies

```shell
cd cz.pycon.org
npm install
```

### Running the site locally

Start the development server:

```shell
cd cz.pycon.org
npm run dev
```

Open http://localhost:4321/2027/ in your browser. The dev server uses hot reload for all changes, so you can edit
the files and see the changes instantly.


### Building the site

To check the production build locally:

```shell
cd cz.pycon.org
npm run build
```

You can safely ignore the deprecation warnings, Boostrap 5 still uses some of the features that are deprecated
in current versions of Sass.
