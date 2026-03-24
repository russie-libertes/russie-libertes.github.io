// // @ts-check
import { defineConfig } from "astro/config";
import sitemap from '@astrojs/sitemap';
import yaml from '@rollup/plugin-yaml';
import tailwindcss from '@tailwindcss/vite';
import { remark } from 'remark';

import { rehypeSplitByHr } from './src/plugins/rehypeSplitByHr.mjs';
import { rehypeImageCarousel } from './src/plugins/rehypeImageCarousel.mjs';
import { remarkExtractHeadingCoverImageIntoFrontmatter } from './src/plugins/remarkExtractHeadingCoverImageIntoFrontmatter.mjs';
import { remarkExtractUrls } from './src/plugins/remarkExtractUrls.mjs';

import SiteConfig from './content/site.config.json';
import markdown_redirects from './content/redirects.md?raw';

const redirects = Object.fromEntries(
  remark().use(remarkExtractUrls).processSync(markdown_redirects).data.urlList
  .map(({caption, url}) => [caption, url])
);

const siteurl = SiteConfig.siteurl;

export default defineConfig({
  site: siteurl,
  build: {concurrency: 4},
  integrations: [
    sitemap({
      filter: (page) =>
        !page.endsWith('/admin/') && 
        !page.endsWith('/admin') && 
        !page.endsWith('/admin/index.html')
      })
  ],
  compressHTML: false,
  vite: {
    plugins: [yaml(), tailwindcss()]
  },
  i18n: SiteConfig.i18n,
  redirects: redirects,
  markdown: {
    remarkPlugins: [
      remarkExtractHeadingCoverImageIntoFrontmatter
    ],
    rehypePlugins: [
      rehypeImageCarousel,
      rehypeSplitByHr,
    ]
  },
})