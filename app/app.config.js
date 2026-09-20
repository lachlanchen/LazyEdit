const base = require('./app.json');
module.exports = () => ({
  ...base.expo,
  ...(process.env.LAZYEDIT_REMOTE_STUDIO === '1' ? {
    name: 'LazyEdit Studio',
    slug: 'lazyedit-studio',
    web: { ...base.expo.web, output: 'single' },
  } : {}),
});
