import type { NodeProps, NodeTypes } from '@xyflow/react';
import { Handle, Position } from '@xyflow/react';
import type { BuffGraphFlowNode } from './specToReactFlow';

const familyClass: Record<string, string> = {
  trigger: 'border-[#D5B236] bg-[#FFF8D8]',
  condition: 'border-[#8FB9E8] bg-[#EDF6FF]',
  read: 'border-[#9CCBA5] bg-[#EFFAF1]',
  effect: 'border-[#F0A37E] bg-[#FFF0E8]',
  state: 'border-[#B8A2E8] bg-[#F5F0FF]',
  compose: 'border-[#A7ADB7] bg-[#F4F6F8]',
};

const BuffGraphNode = ({ data, selected }: NodeProps<BuffGraphFlowNode>) => {
  const specNode = data.specNode;
  return (
    <div
      className={[
        'min-w-[168px] rounded-[8px] border bg-white px-[10px] py-[8px] shadow-sm',
        familyClass[specNode.family] ?? familyClass.compose,
        selected ? 'ring-2 ring-[#F5C542]' : '',
      ].join(' ')}
    >
      <Handle type="target" position={Position.Left} id="in" />
      <div className="text-[10px] uppercase tracking-normal text-[#666]">{specNode.family}</div>
      <div className="mt-[3px] max-w-[148px] truncate text-[13px] font-medium text-[#222]">
        {specNode.display_name}
      </div>
      <div className="mt-[3px] max-w-[148px] truncate text-[11px] text-[#777]">
        {specNode.adapter_id}
      </div>
      <Handle type="source" position={Position.Right} id="out" />
    </div>
  );
};

export const nodeTypes: NodeTypes = {
  buffGraphNode: BuffGraphNode,
};
