import { useState } from 'react';
import type { BuffGraphParityMatrix } from '../api/buffGraphClient';
import { buffGraphClient } from '../api/buffGraphClient';

type ParityMatrixViewProps = {
  matrix?: BuffGraphParityMatrix;
  loading: boolean;
  error?: string;
};

export const ParityMatrixView = ({ matrix, loading, error }: ParityMatrixViewProps) => {
  const [runResult, setRunResult] = useState<BuffGraphParityMatrix>();
  const [runError, setRunError] = useState<string>();
  const [running, setRunning] = useState(false);

  const requestRun = async () => {
    setRunning(true);
    setRunError(undefined);
    try {
      setRunResult(await buffGraphClient.requestParityMatrixRun());
    } catch (nextError) {
      setRunError(nextError instanceof Error ? nextError.message : String(nextError));
    } finally {
      setRunning(false);
    }
  };

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
        <div className="flex items-start justify-between gap-[12px]">
          <div className="min-w-0">
            <div className="text-[11px] uppercase text-[#777]">Status</div>
            <div className="mt-[4px] break-words text-[20px] leading-[26px] text-[#222]">
              {runResult?.status ?? matrix?.status ?? 'not_available'}
            </div>
          </div>
          <button
            type="button"
            className="h-[30px] shrink-0 rounded-[8px] bg-[#202020] px-[10px] text-[12px] text-white hover:bg-[#343434] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={running || !matrix?.required_command}
            onClick={() => void requestRun()}
          >
            {running ? 'Running' : 'Run Matrix'}
          </button>
        </div>
        <div className="mt-[8px] text-[13px] leading-[19px] text-[#666]">
          {runResult?.reason ?? matrix?.reason ?? 'Parity matrix has not been produced yet.'}
        </div>
        {(runResult?.required_command || matrix?.required_command) ? (
          <code className="mt-[10px] block overflow-auto rounded-[6px] bg-white p-[8px] text-[12px] text-[#333]">
            {runResult?.required_command ?? matrix?.required_command}
          </code>
        ) : null}
        {runResult?.run_id ? (
          <div className="mt-[10px] rounded-[6px] border border-[#E6E6E6] bg-white p-[8px] text-[12px] leading-[18px] text-[#555]">
            <div className="font-medium text-[#333]">{runResult.run_id}</div>
            <div>{runResult.evidence_path}</div>
            <div>full_parity_verified: {String(runResult.full_parity_verified)}</div>
          </div>
        ) : null}
        {runError ? (
          <div className="mt-[10px] rounded-[6px] border border-[#F0C3B5] bg-[#FFF1EC] p-[8px] text-[12px] text-[#A23C1B]">
            {runError}
          </div>
        ) : null}
      </div>
    </div>
  );
};
