import { useMemo, useState } from 'react';
import type { BuffGraphTemplate, BuffGraphTemplateInput } from '../templates/buffGraphTemplates';
import { buffGraphTemplates } from '../templates/buffGraphTemplates';

type TemplateWizardProps = {
  onApplyTemplate: (template: BuffGraphTemplate, input: BuffGraphTemplateInput) => void;
};

const defaultInput: BuffGraphTemplateInput = {
  graphId: 'visual-draft',
  displayName: 'Visual Draft',
  ownerName: 'Unassigned',
  sourceBuffIndex: 'Buff-Template-Draft',
};

export const TemplateWizard = ({ onApplyTemplate }: TemplateWizardProps) => {
  const [selectedTemplateId, setSelectedTemplateId] = useState(buffGraphTemplates[0].template_id);
  const [input, setInput] = useState<BuffGraphTemplateInput>(defaultInput);
  const selectedTemplate = useMemo(
    () =>
      buffGraphTemplates.find(template => template.template_id === selectedTemplateId) ??
      buffGraphTemplates[0],
    [selectedTemplateId],
  );

  const updateInput = (key: keyof BuffGraphTemplateInput, value: string) => {
    setInput(current => ({ ...current, [key]: value }));
  };

  return (
    <div className="buff-graph-template-wizard">
      <div className="buff-graph-panel-title">Template</div>
      <div className="grid gap-[8px]">
        {buffGraphTemplates.map(template => (
          <button
            key={template.template_id}
            type="button"
            className={[
              'rounded-[8px] border p-[8px] text-left',
              template.template_id === selectedTemplateId
                ? 'border-[#F5C542] bg-[#FFF8D8]'
                : 'border-[#E6E6E6] bg-white hover:border-[#D6BA4A]',
            ].join(' ')}
            onClick={() => setSelectedTemplateId(template.template_id)}
          >
            <div className="truncate text-[12px] font-medium text-[#222]">{template.display_name}</div>
            <div className="mt-[2px] truncate text-[10px] uppercase text-[#777]">{template.pattern}</div>
          </button>
        ))}
      </div>
      <div className="mt-[10px] grid gap-[7px]">
        <input
          className="buff-graph-input"
          value={input.graphId}
          onChange={event => updateInput('graphId', event.target.value)}
          placeholder="graph id"
        />
        <input
          className="buff-graph-input"
          value={input.displayName}
          onChange={event => updateInput('displayName', event.target.value)}
          placeholder="display name"
        />
        <input
          className="buff-graph-input"
          value={input.ownerName}
          onChange={event => updateInput('ownerName', event.target.value)}
          placeholder="owner"
        />
        <input
          className="buff-graph-input"
          value={input.sourceBuffIndex}
          onChange={event => updateInput('sourceBuffIndex', event.target.value)}
          placeholder="source Buff index"
        />
      </div>
      <button
        type="button"
        className="mt-[10px] h-[32px] w-full rounded-[8px] bg-[#202020] text-[12px] text-white hover:bg-[#343434]"
        onClick={() => onApplyTemplate(selectedTemplate, input)}
      >
        Generate Graph
      </button>
    </div>
  );
};
