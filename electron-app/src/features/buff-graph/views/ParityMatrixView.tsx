import type { BuffGraphParityMatrix } from '../api/buffGraphClient';

type ParityMatrixViewProps = {
  matrix?: BuffGraphParityMatrix;
  loading: boolean;
  error?: string;
};

export const ParityMatrixView = ({ matrix, loading, error }: ParityMatrixViewProps) => {
  if (loading) {
    return <div className="p-[16px] text-[13px] text-[#666]">Loading matrix...</div>;
  }

  if (error) {
    return (
      <div className="m-[16px] rounded-[8px] border border-[#F0C3B5] bg-[#FFF1EC] p-[12px] text-[13px] text-[#A23C1B]">
        {error}
      </div>
    );
  }

  return (
    <div data-buff-graph-view="parity-matrix" className="min-h-0 flex-1 overflow-auto p-[16px]">
      <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[14px]">
        <div className="text-[11px] uppercase text-[#777]">Status</div>
        <div className="mt-[4px] text-[20px] leading-[26px] text-[#222]">
          {matrix?.status ?? 'not_available'}
        </div>
        <div className="mt-[8px] text-[13px] leading-[19px] text-[#666]">
          {matrix?.reason ?? 'Parity matrix has not been produced yet.'}
        </div>
        {matrix?.required_command ? (
          <code className="mt-[10px] block overflow-auto rounded-[6px] bg-white p-[8px] text-[12px] text-[#333]">
            {matrix.required_command}
          </code>
        ) : null}
      </div>
    </div>
  );
};
