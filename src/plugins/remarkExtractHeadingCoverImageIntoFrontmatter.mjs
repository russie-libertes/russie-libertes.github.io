import { toString } from 'mdast-util-to-string';

export function remarkExtractHeadingCoverImageIntoFrontmatter() {
  return function (tree, file) {
    const frontmatter = file.data.astro.frontmatter;

    // 1. Extract the first heading as the title (if not already set)
    if (!frontmatter.title) {
      const headingNode = tree.children.find(
        (node) => node.type === 'heading' && node.depth === 1
      );

      if (headingNode) {
        frontmatter.title = toString(headingNode);
      }
    }

    // 2. Extract the first image as the cover image URL (if not already set)
    if (!frontmatter.coverImage) {
      const imageNode = tree.children.find((node) => node.type === 'image');

      if (imageNode) {
        frontmatter.coverImage = imageNode.url;
      }
    }
  };
}