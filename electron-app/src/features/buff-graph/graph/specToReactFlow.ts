import type { Edge, Node, Viewport } from '@xyflow/react';
import type { BuffGraphEdge, BuffGraphNode, BuffGraphSpec } from '../api/buffGraphClient';

export type BuffGraphViewState = {
  positions: Record<string, { x: number; y: number }>;
  viewport: Viewport;
};

export type BuffGraphNodeData = {
  specNode: BuffGraphNode;
};

export type BuffGraphFlowNode = Node<BuffGraphNodeData, 'buffGraphNode'>;
export type BuffGraphFlowEdge = Edge<{ specEdge: BuffGraphEdge }, 'buffGraphEdge'>;

const familyOrder = ['trigger', 'condition', 'read', 'effect', 'state', 'compose'];

const defaultPosition = (node: BuffGraphNode, index: number) => {
  const familyIndex = Math.max(0, familyOrder.indexOf(node.family));
  return {
    x: 40 + familyIndex * 210,
    y: 40 + index * 96,
  };
};

export const specToReactFlow = (
  spec: BuffGraphSpec,
  viewState?: Partial<BuffGraphViewState>,
): { nodes: BuffGraphFlowNode[]; edges: BuffGraphFlowEdge[] } => ({
  nodes: spec.nodes.map((node, index) => ({
    id: node.node_id,
    type: 'buffGraphNode',
    position: viewState?.positions?.[node.node_id] ?? defaultPosition(node, index),
    data: { specNode: node },
  })),
  edges: spec.edges.map(edge => ({
    id: edge.edge_id,
    type: 'buffGraphEdge',
    source: edge.source_node_id,
    target: edge.target_node_id,
    sourceHandle: edge.source_port,
    targetHandle: edge.target_port,
    data: { specEdge: edge },
  })),
});
