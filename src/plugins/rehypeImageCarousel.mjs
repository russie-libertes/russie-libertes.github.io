import { visit } from 'unist-util-visit';

export function rehypeImageCarousel() {
    return (tree) => {
      visit(tree, 'element', (node, index, parent) => {
        
        /*if(node.tagName === 'ul')
        {
            console.log('parent:', parent);

            if (!node.properties) {
                node.properties = {};
              }
              if (!node.properties.className) {
                node.properties.className = [];
              } else if (typeof node.properties.className === 'string') {
                node.properties.className = [node.properties.className];
              }
              node.properties.className.push('my-custom-class');
        }*/
        

      if (
          //(parent && parent.properties && (parent.properties.className || []).includes('carousel-holder'))
          node.tagName === 'ul' 
          && node.children.every(child => child.type == 'text' || (child.type === 'element' && child.tagName === 'li' && child.children.some(grandchild => grandchild.type === 'element' && grandchild.tagName === 'img')))
         ) {

          const carouselItems = [];
          node.children.forEach((li) => {
            if(li.tagName !== 'li') return;

            const imgNode = li.children.find(child => child.tagName === 'img');
            if (imgNode) {
              const figureChildren = [imgNode];
              if (imgNode.properties.alt) {
                figureChildren.push({
                  type: 'element',
                  tagName: 'figcaption',
                  children: [{ type: 'text', value: imgNode.properties.alt }],
                });
              }
  
              carouselItems.push({
                type: 'element',
                tagName: 'figure',
                properties: {}, //{ className: ['carousel-item'] }, // 5. Apply Carousel Item Classes
                children: figureChildren,
              });
            }
          });
  
          // 2. Transform `ul` to Carousel Container
          Object.assign(node, {
            tagName: 'div',
            properties: {}, //{ className: ['carousel-container'] },
            children: carouselItems,
          });
        }
      });
    };
  }


/*
function remarkCarousel() {
  return (tree) => {
    visit(tree, 'list', (node) => {
      // Check if all list items contain only images (wrapped in paragraphs)
      const isImageList = node.children.every((listItem) => {
        const itemChildren = listItem.children;
        // Check for only one child which is either an image or a paragraph containing an image
        if (itemChildren.length !== 1) return false;

        const content = itemChildren[0];
        if (content.type === 'image') return true;
        
        // Handle images wrapped in paragraphs (default behavior for many parsers)
        if (content.type === 'paragraph' && content.children.length === 1 && content.children[0].type === 'image') {
          return true;
        }

        return false;
      });

      // If it's an image list, mark it in the data property
      if (isImageList) {
        node.data = node.data || {};
        node.data.isCarousel = true;
      }
    });
  };
}
*/
