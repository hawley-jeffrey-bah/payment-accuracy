/**
* Compile USWDS
*/
const uswds = require("@uswds/compile");
const { src, dest, series } = require('gulp');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const rename = require('gulp-rename');

uswds.settings.version = 3;

uswds.paths.dist.img = "./_site/assets/img";
uswds.paths.dist.fonts = "./_site/assets/fonts";
uswds.paths.dist.js	= "./_site/assets/js";
uswds.paths.dist.css = "./_site/assets/css";

exports.updateUswds = uswds.updateUswds;

function bundleChart() {
  return src(['./node_modules/chart.js/dist/chart.umd.js', './_site/assets/js/charts.js'])
    .pipe(concat('./_site/assets/js/chartBundle.js'))
    .pipe(uglify()) // Minify
    .pipe(rename({ suffix: '.min' }))
    .pipe(dest('.'));
}

exports.bundleChart = series(bundleChart);