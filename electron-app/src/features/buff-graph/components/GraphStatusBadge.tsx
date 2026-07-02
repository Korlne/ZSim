import type { BuffGraphRuntimeStatus } from '../api/buffGraphClient';

type GraphStatusBadgeProps = {
  status: BuffGraphRuntimeStatus;
};

const labelByStatus: Record<BuffGraphRuntimeStatus, string> = {
  legacy_python: 'Legacy',
  visual_graph_candidate: 'Candidate',
  visual_graph_default: 'Default',
  visual_graph_disabled: 'Disabled',
};

export const GraphStatusBadge = ({ status }: GraphStatusBadgeProps) => (
  <span className="inline-flex h-[22px] items-center rounded-[6px] border border-[#E6E6E6] bg-white px-[7px] text-[11px] text-[#555]">
    {labelByStatus[status]}
  </span>
);
