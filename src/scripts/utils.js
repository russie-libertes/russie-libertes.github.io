import { AstroComponentInstance } from "astro/runtime/server/index.js";
import { i18n } from "astro:config/client";
import { getCollection } from 'astro:content';

const defaultLocale = i18n?.defaultLocale || '';
const locales = i18n?.locales || [];

export function isProd()
{
    return import.meta.env.MODE == 'production';
}

export function extractLocale(filePath)
{
    const filename = filePath.split('/').pop();
    const exts = filename.split('.');
    const locale = exts.length >= 3 ? exts[exts.length - 2] : undefined;
    return locale;
}

export function formatDateTime(datetime, locale)
{
    if(!datetime) return '';
    return datetime.toLocaleString(locale);
}

export function formatDate(datetime, locale)
{
    if(!datetime) return '';
    return datetime.toLocaleDateString(locale);
}


export function getBaseUrlWithTrailingSlash()
{
    const env_baseurl = import.meta.env.BASE_URL;
    const basurl_has_leading_slash = env_baseurl.startsWith('/') ? 1 : 0;
    const basurl_has_trailing_slash = env_baseurl.endsWith('/') ? 1 : 0;
    const basurl_is_trivial = ['', '/'].includes(env_baseurl);
    const baseurl = basurl_is_trivial ? '/' : (env_baseurl.substring(basurl_has_leading_slash, env_baseurl.length - basurl_has_trailing_slash) + '/'); 
    return baseurl;
}

export function filterEntriesByLocale(entries, currentLocale)
{
    return entries.filter(entry => extractLocale(entry.filePath) == currentLocale);
}

export function getCurrentLocale(Astro)
{
    return Astro.currentLocale || defaultLocale;
}

export function getEntrySlug(entry_id)
{
    return entry_id.split('/').pop();
}

export function isDefaultLocale(locale)
{
    return locale === '' || locale === undefined || locale == defaultLocale;
}

export function makeNonDefaultLocalesRoutes(slug)
{
    const non_default_locales = i18n.locales.filter(s => s != i18n.defaultLocale);
    return non_default_locales.map(locale => ({ params: { locale: locale, slug: slug } }));
}

export function sorterByDate(a, b)
{
    if(!a.data.date)
        return 1;
    if(!b.data.date)
        return -1;
    return b.data.date.valueOf() - a.data.date.valueOf();
}

export function getRecentByDate(entries, currentLocale, topK)
{
    return entries.sort(sorterByDate).slice(0, topK);
}

export function excerpt(content, size = 150)
{
    if (!content) return '';
    // Remove URLs
    let txt = content.replace(/https?:\/\/\S+|www\.\S+/g, '');
    // Remove markdown headers/links/emphasis for a nicer preview
    txt = txt.replace(/[#*_`\[\]\(\)!>~-]/g, '');
    // Truncate excerpt text
    txt = txt.length > size ? txt.slice(0, size - 3) + '…' : txt;
    // Prevent super-long words from breaking layout
    return txt.replace(/\S{33,}/g, (w) => w.slice(0, 32) + '…');
}

export async function getTopLevelEntries()
{
    const posts = await getCollection('posts');
    const pages = await getCollection('pages');
    const projects = await getCollection('projects');
    const entries = [...posts, ...pages, ...projects];
    return entries;
}

export function getPages()
{
    const dynamically_imported = import.meta.glob('../pages/[^\[]*.astro', {eager: true});
    const pages = Object.values(dynamically_imported)
        .filter(x => !x.file.endsWith('/admin.astro'));
    return pages;
}

export function getPostsHtml()
{
    const dynamically_imported = import.meta.glob('../../content/posts/[^\[]*.html', {'eager': true, 'query': '?raw', 'import': 'default'});
    const posts = Object.entries(dynamically_imported).map(([key, value]) => ({ file: key, content: value, isHtml: true }));
    return posts;
}

export function getMarkdownEntryForLocale(collection, locale, basename)
{
  const markdownDefault = collection.filter(x => x.filePath.endsWith(`/${basename}`));
  const markdown = collection.filter(x => x.filePath.endsWith(`/${basename.substring(0, basename.length - 3)}.${locale}.md`));
  const markdowns = markdown.concat(markdownDefault);
  return markdowns.length > 0 ? markdowns[0] : {};
}

export function getLocaleIndexRoutes(IndexContent)
{
    const routes = locales.filter(x => x != defaultLocale).map(locale => ({ params: {locale: locale, slug: locale }, props: { entry: IndexContent, isMarkdown: false, contentLocale : locale }}));
    return routes;
}

export function makeMarkdownRoute(entry)
{
    const locale = extractLocale(entry.filePath);
    const slug = locale === undefined ? entry.id : entry.id.substring(0, entry.id.length - locale.length);
    const route = { params: {locale: locale, slug: slug }, props: { entry, isMarkdown: true, contentLocale : locale || defaultLocale }};
    return route;
}

export function makePageRoute(page)
{
    const ext = '.astro';
    const basename = page.file.split('/').pop();
    const locale = extractLocale(basename);
    const slug = locale === undefined ? basename.substring(0, basename.length - ext.length) : basename.substring(0, basename.length - ext.length - locale.length);
    const entry = page;
    const route = { params: {locale: locale, slug: slug }, props: { entry, isMarkdown: false, contentLocale : locale || defaultLocale }};
    return route;
}


export function filterDefaultLocales(routes)
{
    const defaultLocaleRoutes = routes.filter(isRouteDefaultLocale);
    const augmented_routes = [];
    for(const defaultRoute of defaultLocaleRoutes)
    {
        const nonDefaultLocaleRoutes = routes.filter(r => isRouteNonDefaultLocale(r) && r.props.entry.filePath.endsWith(defaultRoute.props.entry.filePath.substring(0, defaultRoute.props.entry.filePath.length - 3) + '.' + r.params.locale + '.md'));
        const localeRoutes = nonDefaultLocaleRoutes.concat([defaultRoute]);
        const contentLocales = locales.filter(locale => localeRoutes.some(r => r.params.locale == locale || (locale == defaultLocale && r.params.locale === undefined)));
        augmented_routes.push({ params: defaultRoute.params, props: {entry : defaultRoute.props.entry, contentLocales : contentLocales, contentLocale : defaultRoute.props.contentLocale, isMarkdown : defaultRoute.props.isMarkdown}});
    }
    return augmented_routes;
}

export function filterNonDefaultLocales(routes)
{
    const defaultLocaleRoutes = routes.filter(isRouteDefaultLocale);
    const augmented_routes = [];
    for(const defaultRoute of defaultLocaleRoutes)
    {
        const nonDefaultLocaleRoutes = routes.filter(r => isRouteNonDefaultLocale(r) && r.props.entry.filePath.endsWith(defaultRoute.props.entry.filePath.substring(0, defaultRoute.props.entry.filePath.length - 3) + '.' + r.params.locale + '.md'));
        const localeRoutes = nonDefaultLocaleRoutes.concat([defaultRoute]);
        const contentLocales = locales.filter(locale => localeRoutes.some(r => r.params.locale == locale || (locale == defaultLocale && r.params.locale === undefined)));
        for(const locale of locales)
        {
            if(locale == defaultLocale)
                continue;
            const found_routes = nonDefaultLocaleRoutes.filter(r => r.params.locale == locale);
            if(found_routes.length == 1)
            {
                const nonDefaultRoute = found_routes[0];
                augmented_routes.push({ params: {locale : locale, slug : nonDefaultRoute.params.slug}, props: {entry : nonDefaultRoute.props.entry, contentLocales : contentLocales, contentLocale : nonDefaultRoute.props.contentLocale, isMarkdown : defaultRoute.props.isMarkdown}});
                continue;
            }
            else
            {
                augmented_routes.push({ params: {locale : locale, slug : defaultRoute.params.slug}, props: {entry : defaultRoute.props.entry, contentLocales : contentLocales, contentLocale : defaultRoute.props.contentLocale, isMarkdown : defaultRoute.props.isMarkdown}});
            }
        }
    }
    return augmented_routes;
}

export function isRouteDefaultLocale(route)
{
    return isDefaultLocale(route.params.locale);
}

export function isRouteNonDefaultLocale(route)
{
    return !isRouteDefaultLocale(route);
}
