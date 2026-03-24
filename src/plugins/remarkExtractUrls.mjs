import { visit } from 'unist-util-visit';

export function remarkExtractUrls()
{
    return (tree, file) => {
        file.data.urlList = []
    // Visit all 'link' nodes in the AST
    visit(tree, 'link', (node) => {
      file.data.urlList.push({caption: node.children[0].value, url: node.url})
    });
  }
}