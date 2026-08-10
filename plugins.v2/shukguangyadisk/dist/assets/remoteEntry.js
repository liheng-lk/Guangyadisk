import { dynamicLoadingCss, get as legacyGet, init } from './remoteEntry_legacy.js';

const get = (module) => {
  if (module === './Page') {
    dynamicLoadingCss(['Page-213.css'], false, './Page');
    return import('./__federation_expose_DualLoginPage-213.js').then((mod) => () => mod.default);
  }
  return legacyGet(module);
};

export { dynamicLoadingCss, get, init };
