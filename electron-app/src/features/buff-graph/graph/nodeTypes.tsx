import type { NodeProps, NodeTypes } from '@xyflow/react';
import { BuffGraphNodeChrome } from '../components/BuffGraphNodeChrome';
import type { BuffGraphFlowNode } from './specToReactFlow';

const BuffGraphNode = ({ data, selected }: NodeProps<BuffGraphFlowNode>) => {
  return <BuffGraphNodeChrome node={data.specNode} selected={selected} />;
};

export const nodeTypes: NodeTypes = {
  buffGraphNode: BuffGraphNode,
};
