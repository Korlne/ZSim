import type { BuffGraphCompileResult, BuffGraphValidationResult } from '../api/buffGraphClient';

type GraphValidationPanelProps = {
  validation?: BuffGraphValidationResult;
  compile?: BuffGraphCompileResult;
};

export const GraphValidationPanel = ({ validation, compile }: GraphValidationPanelProps) => (
  <div className="min-h-[110px] rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
    <div className="mb-[8px] text-[12px] font-medium text-[#333]">Validation</div>
    <div className="text-[12px] text-[#666]">
      Schema: {validation ? (validation.valid ? 'valid' : 'invalid') : 'not run'}
    </div>
    <div className="mt-[4px] text-[12px] text-[#666]">
      Compile: {compile ? (compile.compiled ? 'compiled' : 'failed') : 'not run'}
    </div>
    {validation?.errors.length || compile?.errors.length ? (
      <div className="mt-[8px] max-h-[72px] overflow-auto text-[11px] text-[#A23C1B]">
        {[...(validation?.errors ?? []), ...(compile?.errors ?? [])].map((error, index) => (
          <div key={`${error.code ?? 'error'}-${index}`}>{error.message ?? error.code}</div>
        ))}
      </div>
    ) : null}
  </div>
);
