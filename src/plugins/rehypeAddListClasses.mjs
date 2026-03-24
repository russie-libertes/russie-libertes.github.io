import { visit } from 'unist-util-visit';


export function rehypeAddListClasses(options = {}) {
	const { ulClass, liClass, imgClass } = options;
	return function (tree)
	{
		visit(tree, 'element', function (node) {
			if (node.tagName === 'ul' && ulClass) {
			node.properties.className = node.properties.className || [];
			if (!node.properties.className.includes(ulClass)) {
			node.properties.className.push(ulClass);
			}
		}

		if (node.tagName === 'li' && liClass) {
			node.properties.className = node.properties.className || [];
			if (!node.properties.className.includes(liClass)) {
			node.properties.className.push(liClass);
			}
		}

		if (node.tagName === 'img' && imgClass) {
			node.properties.className = node.properties.className || [];
			if (!node.properties.className.includes(imgClass)) {
			node.properties.className.push(imgClass);
			}
		}
	})
  }
}