// FIRST LOAD EVERYTHING NEEDED
import { deleteAsync } from "del";
import gulp from "gulp";
import sass from "gulp-dart-sass";
import sourcemaps from "gulp-sourcemaps";
import postcss from "gulp-postcss";
import autoprefixer from "autoprefixer";
import uncss from "postcss-uncss";
import csso from "gulp-csso";
import browserSync from "browser-sync";
import { spawn } from "node:child_process";

const { series, parallel, src, dest, watch } = gulp;

const browserSyncInstance = browserSync.create();

// DEFINE FUNCTIONS

// 1) functions to delete parts of generated files in generated folder

// delete all files
const cleanupAll = () =>
    deleteAsync([
        "static/generated/**/*", // delete all files from /dist/
        "!static/generated/**/.gitkeep", // except HTML, CSS and CSS map files
    ]);

// delete all CSS files and their sourcemaps
const cleanupCss = () => deleteAsync("static/generated/**/*.{css,css.map}");

const copyStatic = () =>
    src([
        "node_modules/bootstrap/dist/js/bootstrap.bundle.min.js", // get JS bundle from currently used Bootstrap
        // Sourcemap is also required, because it is referenced from comment in bootstrap.bundle.min.js:
        "node_modules/bootstrap/dist/js/bootstrap.bundle.min.js.map",
        // "node_modules/bootstrap/dist/js/bootstrap.min.js",
    ]).pipe(dest("static/generated"));

// 2) functions that generate files

// create and process CSS
const sassCompile = () =>
    src("static_src/scss/index.scss") // this is the source for compilation
        .pipe(sourcemaps.init()) // initalizes a sourcemap
        .pipe(sass.sync().on("error", sass.logError)) // compile SCSS to CSS and also tell us about a problem if happens
        .pipe(
            postcss([
                autoprefixer, // automatically adds vendor prefixes if needed
                // see browserslist in package.json for included browsers
                // Official Bootstrap browser support policy:
                // https://getbootstrap.com/docs/5.3/getting-started/browsers-devices/#supported-browsers
            ])
        )
        .pipe(csso()) // compresses CSS
        .pipe(sourcemaps.write("./")) // writes the sourcemap
        .pipe(dest("static/generated")) // destination of the resulting CSS
        .pipe(browserSyncInstance.stream()); // tell browsersync to inject compiled CSS

// remove unused CSS (classes not used in HTML)
const removeUnusedCss = () =>
    src("static/generated/index.css", { allowEmpty: true })
        .pipe(
            postcss([
                uncss({
                    html: ["templates/**/*.html"],
                    media: ["print"], // process additional media queries
                    ignore: [], // provide a list of selectors that should not be removed by UnCSS
                }),
            ])
        )
        .pipe(dest("static/generated"));

// 3) functions to watch and serve

// Run Docker (Django server)
const runServer = (cb) => {
    const cmd = spawn("make", ["up"], { stdio: "inherit" });
    cmd.on("close", function (code) {
        console.log("runServer exited with code " + code);
        cb(code);
    });
};

// development with automatic refreshing after changes to CSS, templates or static files
const startBrowsersync = () =>
    browserSyncInstance.init({
        // initalize Browsersync
        port: 3366, // set different port
        open: false, // don’t open browser
        ghostMode: false, // clicks, scrolls & form inputs on any device will not be mirrored to all others
        reloadOnRestart: true, // reload each browser when Browsersync is restarted

        proxy: {
            target: "localhost:8000",
            cookies: { stripDomain: false },
            proxyReq: [
                (proxyReq, req) => {
                    // Assign proxy 'host' header same as current request at Browsersync server
                    proxyReq.setHeader("Host", req.headers.host);
                },
            ],
        },
    });

// a function to reload Browsersync
const reloadBrowserSync = (cb) => {
    browserSyncInstance.reload();
    cb();
};

// a function to watch for changes
const watchFiles = () => {
    // SCSS changed: run task to compile it again
    watch("static_src/scss/**/*", processCss);
    // templates or data file changed: run task to generate HTML again and reload
    watch(["templates/**/*.html"], reloadBrowserSync);
    // static files changed  (except the generated part): reload
    watch(["static/**/*", "!static/generated/**/*"], reloadBrowserSync);
};

// COMPOSE TASKS

const processCss = series(cleanupCss, sassCompile);

// EXPORT PUBLICLY AVAILABLE TASKS
// These tasks can be run with `npx gulp TASKNAME` on command line for example `npx gulp develop`.
// We use them in npm scripts with `gulp TASKNAME` (see package.json).

// development with automatic refreshing (doesn't remove unused CSS)
export const develop = series(cleanupAll, copyStatic, sassCompile, parallel(runServer, startBrowsersync, watchFiles));

// build everything for production
export const build = series(cleanupAll, copyStatic, sassCompile /*removeUnusedCss*/); // todo: make uncss work

// the default task runs when you run just `gulp`
export default build;
