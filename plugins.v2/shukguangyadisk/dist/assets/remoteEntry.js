import { dynamicLoadingCss, get as legacyGet, init } from './remoteEntry_legacy.js';

const get = (module) => {
  if (module === './Page') {
    dynamicLoadingCss(['Page-76c96a1e.css'], false, './Page');
    return import('./__federation_expose_DualLoginPage.js').then((mod) => () => mod.default);
  }
  return legacyGet(module);
};

export { dynamicLoadingCss, get, init };
