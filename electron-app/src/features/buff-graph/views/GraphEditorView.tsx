import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react';
import type { Connection } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import '../styles.css';
import { buffGraphClient } from '../api/buffGraphClient';
import type {
  BuffGraphCatalogBlock,
  BuffGraphCompileResult,
  BuffGraphMigrationCatalog,
  BuffGraphParityResult,
  BuffGraphSpec,
  BuffGraphSpecSummary,
  BuffGraphValidationResult,
} from '../api/buffGraphClient';
import { GraphParityPanel } from '../components/GraphParityPanel';
import { GraphStatusBadge } from '../components/GraphStatusBadge';
import { GraphValidationPanel } from '../components/GraphValidationPanel';
import { NodeInspector } from '../components/NodeInspector';
import { NodePalette } from '../components/NodePalette';
import { TemplateWizard } from '../components/TemplateWizard';
import { BuffGraphWorkbenchLayout } from '../components/BuffGraphWorkbenchLayout';
import { edgeTypes } from '../graph/edgeTypes';
import { nodeTypes } from '../graph/nodeTypes';
import { reactFlowToSpec, reactFlowToViewState } from '../graph/reactFlowToSpec';
import { specToReactFlow } from '../graph/specToReactFlow';
import type { BuffGraphFlowEdge, BuffGraphFlowNode } from '../graph/specToReactFlow';
import type { BuffGraphTemplate, BuffGraphTemplateInput } from '../templates/buffGraphTemplates';

type GraphEditorViewProps = {
  graphs: BuffGraphSpecSummary[];
  catalog?: BuffGraphMigrationCatalog;
  refresh: () => Promise<void>;
};

const createDraftSpec = (): BuffGraphSpec => ({
  schema_version: 'buffgraphspec.v1',
  node_library_version: 'buffgraphblocks.v1',
  adapter_contract_version: 'buffgraph-adapters.v1',
  graph_id: 'visual-draft',
  display_name: 'Visual Draft',
  owner_kind: 'unknown',
  owner_name: 'Unassigned',
  runtime_status: 'legacy_python',
  nodes: [],
  edges: [],
  params: {},
  parity_metadata: {},
});

const GraphEditorCanvas = ({ graphs, catalog, refresh }: GraphEditorViewProps) => {
  const initialSpec = useMemo(createDraftSpec, []);
  const [spec, setSpec] = useState<BuffGraphSpec>(initialSpec);
  const initialFlow = useMemo(() => specToReactFlow(initialSpec), [initialSpec]);
  const [nodes, setNodes, onNodesChange] = useNodesState<BuffGraphFlowNode>(initialFlow.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<BuffGraphFlowEdge>(initialFlow.edges);
  const [selectedNodeId, setSelectedNodeId] = useState<string>();
  const [validation, setValidation] = useState<BuffGraphValidationResult>();
  const [compileResult, setCompileResult] = useState<BuffGraphCompileResult>();
  const [parity, setParity] = useState<BuffGraphParityResult>();
  const [message, setMessage] = useState<string>();
  const reactFlow = useReactFlow();

  const selectedNode = useMemo(
    () => nodes.find(node => node.id === selectedNodeId)?.data.specNode,
    [nodes, selectedNodeId],
  );

  const materializeSpec = useCallback(() => {
    const nextSpec = reactFlowToSpec(spec, nodes, edges);
    const viewState = reactFlowToViewState(nodes, reactFlow.getViewport());
    return {
      ...nextSpec,
      parity_metadata: {
        ...nextSpec.parity_metadata,
        view_state: viewState,
      },
    };
  }, [edges, nodes, reactFlow, spec]);

  useEffect(() => {
    if (!graphs[0]) return;
    setSpec(current => ({
      ...current,
      graph_id: graphs[0].graph_id || current.graph_id,
      display_name: graphs[0].display_name || current.display_name,
      owner_kind: graphs[0].owner_kind || current.owner_kind,
      owner_name: graphs[0].owner_name || current.owner_name,
      runtime_status: graphs[0].runtime_status,
    }));
  }, [graphs]);

  const onConnect = useCallback(
    (connection: Connection) => {
      const edgeId = `edge-${connection.source ?? 'source'}-${connection.target ?? 'target'}-${Date.now()}`;
      setEdges(current =>
        addEdge(
          {
            ...connection,
            id: edgeId,
            type: 'buffGraphEdge',
            data: {
              specEdge: {
                edge_id: edgeId,
                source_node_id: connection.source ?? '',
                target_node_id: connection.target ?? '',
                source_port: connection.sourceHandle ?? 'out',
                target_port: connection.targetHandle ?? 'in',
              },
            },
          },
          current,
        ),
      );
    },
    [setEdges],
  );

  const addBlock = (block: BuffGraphCatalogBlock) => {
    const nodeId = `${block.block_id.replace(/\W+/g, '-')}-${nodes.length + 1}`;
    setNodes(current => [
      ...current,
      {
        id: nodeId,
        type: 'buffGraphNode',
        position: { x: 80 + current.length * 28, y: 80 + current.length * 32 },
        data: {
          specNode: {
            node_id: nodeId,
            family: block.family,
            block_id: block.block_id,
            adapter_id: block.adapter_id,
            params: {},
            display_name: block.display_name,
          },
        },
      },
    ]);
    setSelectedNodeId(nodeId);
  };

  const applyTemplate = (template: BuffGraphTemplate, input: BuffGraphTemplateInput) => {
    const nextSpec = template.createSpec(input);
    const nextFlow = specToReactFlow(nextSpec);
    setSpec(nextSpec);
    setNodes(nextFlow.nodes);
    setEdges(nextFlow.edges);
    setSelectedNodeId(nextFlow.nodes[0]?.id);
    setValidation(undefined);
    setCompileResult(undefined);
    setParity(undefined);
    setMessage(`${template.display_name} generated`);
    window.requestAnimationFrame(() => reactFlow.fitView({ padding: 0.18 }));
  };

  const updateSelectedParams = (params: Record<string, unknown>) => {
    if (!selectedNodeId) return;
    setNodes(current =>
      current.map(node =>
        node.id === selectedNodeId
          ? { ...node, data: { specNode: { ...node.data.specNode, params } } }
          : node,
      ),
    );
  };

  const save = async () => {
    const nextSpec = materializeSpec();
    const saved = graphs.some(graph => graph.graph_id === nextSpec.graph_id)
      ? await buffGraphClient.updateGraph(nextSpec)
      : await buffGraphClient.saveGraph(nextSpec);
    setSpec(saved);
    setMessage('Saved');
    await refresh();
  };

  const validate = async () => {
    const saved = await buffGraphClient.saveGraph(materializeSpec());
    setSpec(saved);
    const [nextValidation, nextCompile] = await Promise.all([
      buffGraphClient.validateGraph(saved.graph_id),
      buffGraphClient.compileGraph(saved.graph_id),
    ]);
    setValidation(nextValidation);
    setCompileResult(nextCompile);
    setMessage(nextValidation.valid && nextCompile.compiled ? 'Valid' : 'Needs changes');
    await refresh();
  };

  const requestParity = async () => {
    const saved = await buffGraphClient.saveGraph(materializeSpec());
    setSpec(saved);
    setParity(await buffGraphClient.requestParity(saved.graph_id));
  };

  return (
    <BuffGraphWorkbenchLayout
      left={
        <>
          <TemplateWizard onApplyTemplate={applyTemplate} />
          <NodePalette blocks={catalog?.blocks ?? []} onAddBlock={addBlock} />
        </>
      }
      center={
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={(_, node) => setSelectedNodeId(node.id)}
          fitView
        >
          <Background />
          <MiniMap pannable zoomable />
          <Controls />
        </ReactFlow>
      }
      right={
        <div className="flex h-full min-h-0 flex-col overflow-hidden">
        <div className="shrink-0 border-b border-[#E6E6E6] p-[10px]">
          <div className="flex items-center justify-between gap-[8px]">
            <div className="min-w-0">
              <div className="truncate text-[13px] font-medium text-[#222]">{spec.display_name}</div>
              <div className="truncate text-[11px] text-[#777]">{spec.graph_id}</div>
            </div>
            <GraphStatusBadge status={spec.runtime_status} />
          </div>
          <div className="mt-[10px] flex gap-[6px]">
            <button className="h-[30px] rounded-[8px] bg-[#202020] px-[10px] text-[12px] text-white" type="button" onClick={() => void save()}>
              Save
            </button>
            <button className="h-[30px] rounded-[8px] bg-[#F5C542] px-[10px] text-[12px] text-[#222]" type="button" onClick={() => void validate()}>
              Validate
            </button>
            <button className="h-[30px] rounded-[8px] border border-[#DCDCDC] px-[10px] text-[12px] text-[#333]" type="button" onClick={() => void requestParity()}>
              Parity
            </button>
          </div>
          {message ? <div className="mt-[8px] text-[11px] text-[#666]">{message}</div> : null}
        </div>
        <div className="min-h-0 flex-1 overflow-hidden">
          <NodeInspector node={selectedNode} onParamsChange={updateSelectedParams} />
        </div>
        <div className="grid shrink-0 gap-[8px] border-t border-[#E6E6E6] p-[8px]">
          <GraphValidationPanel validation={validation} compile={compileResult} />
          <GraphParityPanel parity={parity} />
        </div>
      </div>
      }
    />
  );
};

export const GraphEditorView = (props: GraphEditorViewProps) => (
  <ReactFlowProvider>
    <GraphEditorCanvas {...props} />
  </ReactFlowProvider>
);
