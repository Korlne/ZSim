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

export type BuffGraphParityMatrix = {
  status: 'not_available';
  reason: string;
  required_command?: string | null;
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
  return {
    status: 'not_available',
    reason: String(item.reason ?? 'Parity matrix is not available yet.'),
    required_command:
      item.required_command === undefined || item.required_command === null
        ? undefined
        : String(item.required_command),
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

  async getParityMatrix(): Promise<BuffGraphParityMatrix> {
    const response = await requireApiClient().get('/api/buff-graphs/parity/matrix');
    return normalizeMatrix(parseDataResponse<unknown>(response, 'Read Buff graph parity matrix'));
  },
};
