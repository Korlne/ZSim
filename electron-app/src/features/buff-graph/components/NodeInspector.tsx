import type { BuffGraphNode } from '../api/buffGraphClient';

type NodeInspectorProps = {
  node?: BuffGraphNode;
  onParamsChange: (params: Record<string, unknown>) => void;
};

export const NodeInspector = ({ node, onParamsChange }: NodeInspectorProps) => {
  if (!node) {
    return <div className="p-[10px] text-[12px] text-[#777]">No node selected</div>;
  }

  const paramsText = JSON.stringify(node.params, null, 2);

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden">
      <div className="shrink-0 border-b border-[#E6E6E6] p-[10px]">
        <div className="truncate text-[13px] font-medium text-[#222]">{node.display_name}</div>
        <div className="mt-[2px] truncate text-[11px] text-[#777]">{node.block_id}</div>
      </div>
      <div className="min-h-0 flex-1 overflow-auto p-[10px]">
        <label className="text-[11px] uppercase text-[#777]" htmlFor="buff-graph-node-params">
          Params
        </label>
        <textarea
          id="buff-graph-node-params"
          className="mt-[6px] h-[180px] w-full resize-none rounded-[8px] border border-[#DCDCDC] bg-white p-[8px] font-mono text-[12px] text-[#333]"
          value={paramsText}
          onChange={event => {
            try {
              const parsed = JSON.parse(event.target.value) as Record<string, unknown>;
              onParamsChange(parsed && typeof parsed === 'object' ? parsed : {});
            } catch {
              // Keep the last valid params until the user finishes editing JSON.
            }
          }}
        />
      </div>
    </div>
  );
};
