const path = require('path');
const pkg = require('./package');

module.exports = {
  entry: [
    'src/polyfills.js',
    'src/index.js',
  ],
  html: {
    title: pkg.productName,
    description: pkg.description,
    template: path.join(__dirname, 'index.ejs'),
  },
  postcss: {
    plugins: [
      // Your postcss plugins
    ],
  },
  /* eslint-disable*/
  presets: [
    require('poi-preset-bundle-report')(),
    require('poi-preset-offline')({
      pwa: './src/pwa.js', // Path to pwa runtime entry
      pluginOptions: {}, // Additional options for offline-plugin
    }),
    // require('poi-preset-resolve-alias')({
    // //   vue: path.join(__dirname, '.\\node_modules\\vue\\dist\\vue.js'),
    //   vue$: 'E:/git/InterMarketDemo/client/node_module/vue/index.js'
    // }),
  ],
  transformModules: ['uri-js'],
  /* eslint-enable */
  // resolve: {
  //   alias: {
  //     vue$: 'E:/git/InterMarketDemo/client/node_module/vue/index.js',
  //   },
  // },
};
