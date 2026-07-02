import { Handle, Position } from '@xyflow/react';
import type { BuffGraphNode } from '../api/buffGraphClient';

type BuffGraphNodeChromeProps = {
  node: BuffGraphNode;
  selected?: boolean;
};

const familyLabel: Record<string, string> = {
  trigger: 'Trigger',
  condition: 'Condition',
  read: 'Read',
  effect: 'Effect',
  state: 'State',
  compose: 'Compose',
};

export const BuffGraphNodeChrome = ({ node, selected = false }: BuffGraphNodeChromeProps) => (
  <div
    className={[
      'buff-graph-node',
      `buff-graph-node-${node.family}`,
      selected ? 'buff-graph-node-selected' : '',
    ].join(' ')}
  >
    <Handle type="target" position={Position.Left} id="in" />
    <div className="buff-graph-node-family">{familyLabel[node.family] ?? node.family}</div>
    <div className="buff-graph-node-title">{node.display_name}</div>
    <div className="buff-graph-node-adapter">{node.adapter_id}</div>
    <Handle type="source" position={Position.Right} id="out" />
  </div>
);
