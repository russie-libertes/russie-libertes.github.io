import { visit } from 'unist-util-visit';
import { h } from 'hastscript';

export function rehypeSplitByHr() {
  return (tree) => {
    if (!tree.children) {
      return;
    }

    let newChildren = [];
    let currentGroup = [];

    let has_hr = false;
    for (const node of tree.children) {
      // Check if the node is an <hr> tag
      if (node.type === 'element' && node.tagName === 'hr') {
        has_hr = true;
        // If the current group is not empty, wrap it in a div and add to newChildren
        if (currentGroup.length > 0) {
          newChildren.push(h('div', currentGroup));
          currentGroup = []; // Start a new group
        }
        // The <hr> itself is discarded in this implementation. If you want to keep it
        // as a separator outside the divs, you could push it to newChildren here.
      } else {
        // Add non-<hr> nodes to the current group
        currentGroup.push(node);
      }
    }

    if (has_hr) {
      // Wrap the last group if it's not empty
      if (currentGroup.length > 0) {
        newChildren.push(h('div', currentGroup));
      }
    }

    else {
      newChildren = currentGroup;
    }

    // Replace the original children with the new grouped children
    tree.children = newChildren;
  };
}
