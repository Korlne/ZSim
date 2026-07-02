import type { BuffGraphParityResult } from '../api/buffGraphClient';

type GraphParityPanelProps = {
  parity?: BuffGraphParityResult;
};

export const GraphParityPanel = ({ parity }: GraphParityPanelProps) => (
  <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
    <div className="mb-[8px] text-[12px] font-medium text-[#333]">Parity</div>
    <div className="text-[12px] text-[#666]">{parity?.status ?? 'not run'}</div>
    {parity?.reason ? <div className="mt-[6px] text-[11px] leading-[16px] text-[#777]">{parity.reason}</div> : null}
  </div>
);
