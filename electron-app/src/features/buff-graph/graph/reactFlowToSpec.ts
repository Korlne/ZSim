import type { Edge, Node, Viewport } from '@xyflow/react';
import type { BuffGraphEdge, BuffGraphNode, BuffGraphSpec } from '../api/buffGraphClient';
import type { BuffGraphViewState } from './specToReactFlow';

type NodeWithSpec = Node<{ specNode?: BuffGraphNode }>;
type EdgeWithSpec = Edge<{ specEdge?: BuffGraphEdge }>;

export const reactFlowToSpec = (
  spec: BuffGraphSpec,
  nodes: NodeWithSpec[],
  edges: EdgeWithSpec[],
): BuffGraphSpec => ({
  ...spec,
  nodes: nodes.map(node => {
    const specNode = node.data?.specNode;
    return {
      node_id: node.id,
      family: specNode?.family ?? 'compose',
      block_id: specNode?.block_id ?? 'compose.sequence',
      adapter_id: specNode?.adapter_id ?? 'compose.sequence',
      params: specNode?.params ?? {},
      display_name: specNode?.display_name ?? node.id,
    };
  }),
  edges: edges.map(edge => ({
    edge_id: edge.id,
    source_node_id: edge.source,
    target_node_id: edge.target,
    source_port: edge.sourceHandle ?? edge.data?.specEdge?.source_port ?? 'out',
    target_port: edge.targetHandle ?? edge.data?.specEdge?.target_port ?? 'in',
  })),
});

export const reactFlowToViewState = (
  nodes: NodeWithSpec[],
  viewport: Viewport,
): BuffGraphViewState => ({
  positions: Object.fromEntries(nodes.map(node => [node.id, node.position])),
  viewport,
});
