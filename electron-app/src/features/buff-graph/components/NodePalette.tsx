import type { BuffGraphCatalogBlock } from '../api/buffGraphClient';

type NodePaletteProps = {
  blocks: BuffGraphCatalogBlock[];
  onAddBlock: (block: BuffGraphCatalogBlock) => void;
};

export const NodePalette = ({ blocks, onAddBlock }: NodePaletteProps) => (
  <div className="flex h-full min-h-0 flex-col overflow-hidden">
    <div className="shrink-0 px-[10px] py-[8px] text-[12px] font-medium text-[#333]">Nodes</div>
    <div className="min-h-0 flex-1 overflow-auto px-[8px] pb-[8px]">
      {blocks.map(block => (
        <button
          key={block.block_id}
          type="button"
          className="mb-[6px] block w-full rounded-[8px] border border-[#E6E6E6] bg-white p-[8px] text-left hover:border-[#F5C542]"
          onClick={() => onAddBlock(block)}
        >
          <div className="truncate text-[12px] text-[#222]">{block.display_name}</div>
          <div className="mt-[2px] truncate text-[10px] uppercase text-[#777]">{block.family}</div>
        </button>
      ))}
    </div>
  </div>
);
