if (!window.Promise) {
  /* eslint-disable global-require */
  window.Promise = require('promise-polyfill');
  /* eslint-enable global-require */
}

Object.assign = require('object-assign');
