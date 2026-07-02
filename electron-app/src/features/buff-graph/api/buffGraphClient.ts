type ApiResponse = {
  status: number;
  body: string;
};

type ApiEnvelope = {
  code?: number;
  message?: string;
  data?: unknown;
};

export type BuffGraphRuntimeStatus =
  | 'legacy_python'
  | 'visual_graph_candidate'
  | 'visual_graph_default'
  | 'visual_graph_disabled';

export type BuffGraphSpecSummary = {
  graph_id: string;
  display_name: string;
  owner_kind: string;
  owner_name: string;
  source_buff_index?: string | null;
  created_from_xlogic?: string | null;
  runtime_status: BuffGraphRuntimeStatus;
  last_verified_at?: string | null;
};

export type BuffGraphCatalogBlock = {
  block_id: string;
  family: string;
  display_name: string;
  adapter_id: string;
};

export type BuffGraphMigrationCatalog = {
  block_families: string[];
  blocks: BuffGraphCatalogBlock[];
  custom_python_nodes_allowed: boolean;
};

export type BuffGraphNode = {
  node_id: string;
  family: string;
  block_id: string;
  adapter_id: string;
  params: Record<string, unknown>;
  display_name: string;
};

export type BuffGraphEdge = {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  source_port: string;
  target_port: string;
};

export type BuffGraphSpec = BuffGraphSpecSummary & {
  schema_version: string;
  node_library_version: string;
  adapter_contract_version: string;
  nodes: BuffGraphNode[];
  edges: BuffGraphEdge[];
  params: Record<string, unknown>;
  parity_metadata: Record<string, unknown>;
  last_parity_baseline?: string | null;
};

export type BuffGraphValidationResult = {
  valid: boolean;
  errors: { code?: string; message?: string; node_id?: string }[];
};

export type BuffGraphCompileResult = {
  compiled: boolean;
  errors: { code?: string; message?: string; node_id?: string }[];
  execution_order: string[];
};

export type BuffGraphParityResult = {
  status:
    | 'not_available'
    | 'ready_for_oracle'
    | 'candidate_harness_passed'
    | 'candidate_harness_failed';
  graph_id: string;
  reason: string;
  candidate_harness_id?: string | null;
  candidate_runtime_status?: BuffGraphRuntimeStatus | null;
  candidate_parity_passed?: boolean;
  full_parity_verified?: boolean;
  evidence?: Record<string, unknown>;
};

export type BuffGraphCandidateSliceEvidence = {
  graph_id: string;
  api_endpoint: string;
  status: BuffGraphParityResult['status'];
  full_parity_verified: boolean;
};

export type BuffGraphParityMatrix = {
  status: 'not_available' | 'run_requested';
  reason: string;
  required_command: string;
  evidence_path: string;
  command_status: 'runner_required' | 'request_recorded';
  run_id?: string | null;
  ui_driven: boolean;
  full_simulation_matrix: boolean;
  full_parity_verified: boolean;
  candidate_harness_id?: string | null;
  candidate_runtime_status?: BuffGraphRuntimeStatus | null;
  candidate_parity_passed?: boolean;
  candidate_slice_evidence?: BuffGraphCandidateSliceEvidence;
  matrix_scope: string[];
};

export class BuffGraphApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'BuffGraphApiError';
    this.status = status;
  }
}

const requireApiClient = () => {
  if (!window.apiClient) {
    throw new BuffGraphApiError('ZSim API client is not available');
  }
  return window.apiClient;
};

const parseJsonResponse = (response: ApiResponse, operation: string): unknown => {
  let parsed: unknown = null;

  if (response.body) {
    try {
      parsed = JSON.parse(response.body);
    } catch {
      throw new BuffGraphApiError(`${operation} returned invalid JSON`, response.status);
    }
  }

  if (response.status < 200 || response.status >= 300) {
    const detail =
      parsed && typeof parsed === 'object' && 'detail' in parsed
        ? String((parsed as { detail?: unknown }).detail)
        : response.body || `HTTP ${response.status}`;
    throw new BuffGraphApiError(`${operation} failed: ${detail}`, response.status);
  }

  return parsed;
};

const unwrapData = (payload: unknown): unknown => {
  if (
    payload &&
    typeof payload === 'object' &&
    ('data' in payload || 'code' in payload || 'message' in payload)
  ) {
    return (payload as ApiEnvelope).data;
  }
  return payload;
};

const parseDataResponse = <T,>(response: ApiResponse, operation: string): T =>
  unwrapData(parseJsonResponse(response, operation)) as T;

const unwrapList = <T,>(payload: unknown, keys: string[]): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === 'object') {
    for (const key of keys) {
      const value = (payload as Record<string, unknown>)[key];
      if (Array.isArray(value)) return value as T[];
    }
  }
  return [];
};

const normalizeGraph = (payload: unknown): BuffGraphSpecSummary => {
  const item = (payload && typeof payload === 'object' ? payload : {}) as Record<string, unknown>;
  return {
    graph_id: String(item.graph_id ?? ''),
    display_name: String(item.display_name ?? item.graph_id ?? ''),
    owner_kind: String(item.owner_kind ?? 'unknown'),
    owner_name: String(item.owner_name ?? ''),
    source_buff_index:
      item.source_buff_index === undefined || item.source_buff_index === null
        ? undefined
        : String(item.source_buff_index),
    created_from_xlogic:
      item.created_from_xlogic === undefined || item.created_from_xlogic === null
        ? undefined
        : String(item.created_from_xlogic),
    runtime_status: (item.runtime_status ?? 'legacy_python') as BuffGraphRuntimeStatus,
    last_verified_at:
      item.last_verified_at === undefined || item.last_verified_at === null
        ? undefined
        : String(item.last_verified_at),
  };
};

const normalizeSpec = (payload: unknown): BuffGraphSpec => {
  const item = (payload && typeof payload === 'object' ? payload : {}) as Record<string, unknown>;
  return {
    ...normalizeGraph(item),
    schema_version: String(item.schema_version ?? 'buffgraphspec.v1'),
    node_library_version: String(item.node_library_version ?? 'buffgraphblocks.v1'),
    adapter_contract_version: String(item.adapter_contract_version ?? 'buffgraph-adapters.v1'),
    nodes: Array.isArray(item.nodes)
      ? item.nodes.map(node => {
          const nodeItem =
            node && typeof node === 'object' ? (node as Record<string, unknown>) : {};
          return {
            node_id: String(nodeItem.node_id ?? ''),
            family: String(nodeItem.family ?? ''),
            block_id: String(nodeItem.block_id ?? ''),
            adapter_id: String(nodeItem.adapter_id ?? ''),
            params:
              nodeItem.params && typeof nodeItem.params === 'object' && !Array.isArray(nodeItem.params)
                ? (nodeItem.params as Record<string, unknown>)
                : {},
            display_name: String(nodeItem.display_name ?? nodeItem.block_id ?? ''),
          };
        })
      : [],
    edges: Array.isArray(item.edges)
      ? item.edges.map(edge => {
          const edgeItem =
            edge && typeof edge === 'object' ? (edge as Record<string, unknown>) : {};
          return {
            edge_id: String(edgeItem.edge_id ?? ''),
            source_node_id: String(edgeItem.source_node_id ?? ''),
            target_node_id: String(edgeItem.target_node_id ?? ''),
            source_port: String(edgeItem.source_port ?? 'out'),
            target_port: String(edgeItem.target_port ?? 'in'),
          };
        })
      : [],
    params:
      item.params && typeof item.params === 'object' && !Array.isArray(item.params)
        ? (item.params as Record<string, unknown>)
        : {},
    parity_metadata:
      item.parity_metadata &&
      typeof item.parity_metadata === 'object' &&
      !Array.isArray(item.parity_metadata)
        ? (item.parity_metadata as Record<string, unknown>)
        : {},
    last_parity_baseline:
      item.last_parity_baseline === undefined || item.last_parity_baseline === null
        ? undefined
        : String(item.last_parity_baseline),
  };
};

const normalizeCatalog = (payload: unknown): BuffGraphMigrationCatalog => {
  const item = (payload && typeof payload === 'object' ? payload : {}) as Record<string, unknown>;
  return {
    block_families: Array.isArray(item.block_families) ? item.block_families.map(String) : [],
    blocks: Array.isArray(item.blocks)
      ? item.blocks.map(block => {
          const blockItem =
            block && typeof block === 'object' ? (block as Record<string, unknown>) : {};
          return {
            block_id: String(blockItem.block_id ?? ''),
            family: String(blockItem.family ?? ''),
            display_name: String(blockItem.display_name ?? blockItem.block_id ?? ''),
            adapter_id: String(blockItem.adapter_id ?? ''),
          };
        })
      : [],
    custom_python_nodes_allowed: item.custom_python_nodes_allowed === true,
  };
};

const normalizeMatrix = (payload: unknown): BuffGraphParityMatrix => {
  const item = (payload && typeof payload === 'object' ? payload : {}) as Record<string, unknown>;
  const status = item.status === 'run_requested' ? 'run_requested' : 'not_available';
  const commandStatus =
    item.command_status === 'request_recorded' ? 'request_recorded' : 'runner_required';
  const rawCandidateEvidence =
    item.candidate_slice_evidence && typeof item.candidate_slice_evidence === 'object'
      ? (item.candidate_slice_evidence as Record<string, unknown>)
      : undefined;
  return {
    status,
    reason: String(item.reason ?? 'Parity matrix is not available yet.'),
    required_command:
      item.required_command === undefined || item.required_command === null
        ? ''
        : String(item.required_command),
    evidence_path:
      item.evidence_path === undefined || item.evidence_path === null
        ? ''
        : String(item.evidence_path),
    command_status: commandStatus,
    run_id:
      item.run_id === undefined || item.run_id === null ? undefined : String(item.run_id),
    ui_driven: item.ui_driven === true,
    full_simulation_matrix: item.full_simulation_matrix === true,
    full_parity_verified: item.full_parity_verified === true,
    candidate_harness_id:
      item.candidate_harness_id === undefined || item.candidate_harness_id === null
        ? undefined
        : String(item.candidate_harness_id),
    candidate_runtime_status:
      item.candidate_runtime_status === undefined || item.candidate_runtime_status === null
        ? undefined
        : (String(item.candidate_runtime_status) as BuffGraphRuntimeStatus),
    candidate_parity_passed:
      item.candidate_parity_passed === undefined
        ? undefined
        : item.candidate_parity_passed === true,
    candidate_slice_evidence: rawCandidateEvidence
      ? {
          graph_id: String(rawCandidateEvidence.graph_id ?? ''),
          api_endpoint: String(rawCandidateEvidence.api_endpoint ?? ''),
          status: (
            rawCandidateEvidence.status === 'candidate_harness_passed' ||
            rawCandidateEvidence.status === 'candidate_harness_failed' ||
            rawCandidateEvidence.status === 'ready_for_oracle'
              ? rawCandidateEvidence.status
              : 'not_available'
          ) as BuffGraphParityResult['status'],
          full_parity_verified: rawCandidateEvidence.full_parity_verified === true,
        }
      : undefined,
    matrix_scope: Array.isArray(item.matrix_scope) ? item.matrix_scope.map(String) : [],
  };
};

export const buffGraphClient = {
  async listGraphs(): Promise<BuffGraphSpecSummary[]> {
    const response = await requireApiClient().get('/api/buff-graphs');
    const payload = parseDataResponse<unknown>(response, 'List Buff graphs');
    return unwrapList<unknown>(payload, ['graphs', 'items']).map(normalizeGraph);
  },

  async getMigrationCatalog(): Promise<BuffGraphMigrationCatalog> {
    const response = await requireApiClient().get('/api/buff-graphs/migration/catalog');
    return normalizeCatalog(parseDataResponse<unknown>(response, 'Read Buff graph catalog'));
  },

  async saveGraph(spec: BuffGraphSpec): Promise<BuffGraphSpec> {
    const response = await requireApiClient().post('/api/buff-graphs', { spec });
    return normalizeSpec(parseDataResponse<unknown>(response, 'Save Buff graph'));
  },

  async updateGraph(spec: BuffGraphSpec): Promise<BuffGraphSpec> {
    const response = await requireApiClient().put(`/api/buff-graphs/${spec.graph_id}`, { spec });
    return normalizeSpec(parseDataResponse<unknown>(response, 'Update Buff graph'));
  },

  async validateGraph(graphId: string): Promise<BuffGraphValidationResult> {
    const response = await requireApiClient().post(`/api/buff-graphs/${graphId}/validate`);
    return parseDataResponse<BuffGraphValidationResult>(response, 'Validate Buff graph');
  },

  async compileGraph(graphId: string): Promise<BuffGraphCompileResult> {
    const response = await requireApiClient().post(`/api/buff-graphs/${graphId}/compile`);
    return parseDataResponse<BuffGraphCompileResult>(response, 'Compile Buff graph');
  },

  async requestParity(graphId: string): Promise<BuffGraphParityResult> {
    const response = await requireApiClient().post(`/api/buff-graphs/${graphId}/parity`);
    return parseDataResponse<BuffGraphParityResult>(response, 'Request Buff graph parity');
  },

  async getParityMatrix(): Promise<BuffGraphParityMatrix> {
    const response = await requireApiClient().get('/api/buff-graphs/parity/matrix');
    return normalizeMatrix(parseDataResponse<unknown>(response, 'Read Buff graph parity matrix'));
  },

  async requestParityMatrixRun(): Promise<BuffGraphParityMatrix> {
    const response = await requireApiClient().post('/api/buff-graphs/parity/matrix/run');
    return normalizeMatrix(parseDataResponse<unknown>(response, 'Request Buff graph parity matrix'));
  },
};
