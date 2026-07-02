import type { BuffGraphEdge, BuffGraphNode, BuffGraphSpec } from '../api/buffGraphClient';

export type BuffGraphTemplateSource =
  | 'character'
  | 'w_engine'
  | 'drive_disc'
  | 'cinema'
  | 'core_passive'
  | 'team_effect';

export type BuffGraphTemplate = {
  template_id: string;
  display_name: string;
  source: BuffGraphTemplateSource;
  pattern: string;
  description: string;
  createSpec: (input: BuffGraphTemplateInput) => BuffGraphSpec;
};

export type BuffGraphTemplateInput = {
  graphId: string;
  displayName: string;
  ownerName: string;
  sourceBuffIndex: string;
};

const node = (
  node_id: string,
  family: BuffGraphNode['family'],
  block_id: string,
  adapter_id: string,
  display_name: string,
  params: Record<string, unknown> = {},
): BuffGraphNode => ({
  node_id,
  family,
  block_id,
  adapter_id,
  params,
  display_name,
});

const edge = (
  edge_id: string,
  source_node_id: string,
  target_node_id: string,
  source_port = 'out',
  target_port = 'in',
): BuffGraphEdge => ({
  edge_id,
  source_node_id,
  target_node_id,
  source_port,
  target_port,
});

const spec = (
  input: BuffGraphTemplateInput,
  nodes: BuffGraphNode[],
  edges: BuffGraphEdge[],
): BuffGraphSpec => ({
  schema_version: 'buffgraphspec.v1',
  node_library_version: 'buffgraphblocks.v1',
  adapter_contract_version: 'buffgraph-adapters.v1',
  graph_id: input.graphId,
  display_name: input.displayName,
  owner_kind: 'unknown',
  owner_name: input.ownerName,
  source_buff_index: input.sourceBuffIndex,
  runtime_status: 'legacy_python',
  nodes,
  edges,
  params: {},
  parity_metadata: {
    template_generated: true,
  },
});

export const buffGraphTemplates: BuffGraphTemplate[] = [
  {
    template_id: 'hit-triggered-buff',
    display_name: 'Hit-triggered Buff',
    source: 'character',
    pattern: 'skill hit -> start buff',
    description: 'Starts a target Buff after a selected skill hit event.',
    createSpec: input =>
      spec(
        input,
        [
          node('trigger', 'trigger', 'trigger.skill_hit', 'trigger.skill_hit.v1', 'Skill Hit', {
            skill_tag: 'basic',
          }),
          node('effect', 'effect', 'effect.start_buff', 'effect.start_buff.v1', 'Start Buff', {
            target_buff_index: input.sourceBuffIndex,
          }),
        ],
        [edge('edge-trigger-effect', 'trigger', 'effect', 'event', 'context')],
      ),
  },
  {
    template_id: 'conditional-passive-buff',
    display_name: 'Conditional Passive',
    source: 'core_passive',
    pattern: 'refresh -> condition -> start buff',
    description: 'Checks an existing Buff state before applying a passive effect.',
    createSpec: input =>
      spec(
        input,
        [
          node('refresh', 'trigger', 'trigger.buff_refresh', 'trigger.buff_refresh.v1', 'Buff Refresh', {
            buff_index: input.sourceBuffIndex,
          }),
          node('active', 'condition', 'condition.buff_active', 'condition.buff_active.v1', 'Buff Active', {
            buff_index: input.sourceBuffIndex,
          }),
          node('effect', 'effect', 'effect.start_buff', 'effect.start_buff.v1', 'Start Buff', {
            target_buff_index: input.sourceBuffIndex,
          }),
        ],
        [
          edge('edge-refresh-active', 'refresh', 'active', 'event', 'context'),
          edge('edge-active-effect', 'active', 'effect', 'result', 'condition'),
        ],
      ),
  },
  {
    template_id: 'stack-accumulation',
    display_name: 'Stack Accumulation',
    source: 'cinema',
    pattern: 'skill hit -> update count',
    description: 'Adds to a Buff counter after a hit-triggered condition.',
    createSpec: input =>
      spec(
        input,
        [
          node('trigger', 'trigger', 'trigger.skill_hit', 'trigger.skill_hit.v1', 'Skill Hit', {
            skill_tag: 'basic',
          }),
          node(
            'count',
            'effect',
            'effect.update_buff_count',
            'effect.update_buff_count.v1',
            'Update Count',
            {
              target_buff_index: input.sourceBuffIndex,
              mode: 'add',
            },
          ),
        ],
        [edge('edge-trigger-count', 'trigger', 'count', 'event', 'value')],
      ),
  },
];
