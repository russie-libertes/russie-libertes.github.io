
import { glob, file } from "astro/loaders";
import { z, defineCollection } from "astro:content";

const pages = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: "./content/pages/" }),
  schema: z.object({
    title: z.string().optional(),
    date: z.date().optional(),
  }),
});

const posts = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: "./content/posts/" }),
  schema: ({ image }) => z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    date: z.date().optional(),
    coverImage: image().optional(),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: "./content/projects/" }),
  schema: ({ image }) => z.object({
    title: z.string().optional(),
    description: z.string().optional(),
    coverImage: image().optional(),
  }),
});

const main = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: "./content/main/" }),
  schema: ({ image }) => z.object({
    title: z.string().optional(),
    coverImage: image().optional(),
  }),
});

export const collections = { posts, pages, projects, main };
