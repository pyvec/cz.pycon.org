# Provisional PyCon CZ 2026 website

The provisional website for PyCon CZ 2026 uses [Astro](https://astro.build) to build a static site for the event.
The Astro project is located in the `cz.pycon.org` subdirectory, the static site is in the `public` subdirectory.

The build is currently not automated - to update the site, you have to build a new version locally and the commit
the updated files in the `public` subdirectory.

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

Open http://localhost:4321/2026/ in your browser. The dev server uses hot reload for all changes, so you can edit
the files and see the changes instantly.


### Building the site

The build is not yet automated, so you have to build the site locally:

```shell
cd cz.pycon.org
npm run build
```

You can safely ignore the deprecation warnings, Boostrap 5 still uses some of the features that are deprecated
in current versions of Sass.

Remember to commit the updated files in the `public` subdirectory!
