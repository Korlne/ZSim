import type { BuffGraphMigrationCatalog } from '../api/buffGraphClient';

type MigrationCatalogViewProps = {
  catalog?: BuffGraphMigrationCatalog;
  loading: boolean;
  error?: string;
};

const familyTone: Record<string, string> = {
  trigger: 'border-[#D5B236] bg-[#FFF8D8] text-[#6F5700]',
  condition: 'border-[#8FB9E8] bg-[#EDF6FF] text-[#1F5C99]',
  read: 'border-[#9CCBA5] bg-[#EFFAF1] text-[#2E6B3C]',
  effect: 'border-[#F0A37E] bg-[#FFF0E8] text-[#A74418]',
  state: 'border-[#B8A2E8] bg-[#F5F0FF] text-[#5B3A9A]',
  compose: 'border-[#A7ADB7] bg-[#F4F6F8] text-[#3D4652]',
};

export const MigrationCatalogView = ({ catalog, loading, error }: MigrationCatalogViewProps) => {
  if (loading) {
    return <div className="p-[16px] text-[13px] text-[#666]">Loading catalog...</div>;
  }

  if (error) {
    return (
      <div className="m-[16px] rounded-[8px] border border-[#F0C3B5] bg-[#FFF1EC] p-[12px] text-[13px] text-[#A23C1B]">
        {error}
      </div>
    );
  }

  const blocks = catalog?.blocks ?? [];

  return (
    <div data-buff-graph-view="catalog" className="min-h-0 flex-1 overflow-auto p-[16px]">
      <div className="mb-[12px] grid grid-cols-3 gap-[8px]">
        <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
          <div className="text-[11px] uppercase text-[#777]">Families</div>
          <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">
            {catalog?.block_families.length ?? 0}
          </div>
        </div>
        <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
          <div className="text-[11px] uppercase text-[#777]">Blocks</div>
          <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">{blocks.length}</div>
        </div>
        <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
          <div className="text-[11px] uppercase text-[#777]">Code Nodes</div>
          <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">
            {catalog?.custom_python_nodes_allowed ? 'On' : 'Off'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-[8px]">
        {blocks.map(block => (
          <div
            key={block.block_id}
            className="min-h-[92px] rounded-[8px] border border-[#E6E6E6] bg-white p-[10px]"
          >
            <div
              className={`mb-[8px] inline-flex rounded-[6px] border px-[7px] py-[2px] text-[11px] ${
                familyTone[block.family] ?? familyTone.compose
              }`}
            >
              {block.family}
            </div>
            <div className="truncate text-[14px] font-medium text-[#222]">{block.display_name}</div>
            <div className="mt-[4px] truncate text-[12px] text-[#777]">{block.adapter_id}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
