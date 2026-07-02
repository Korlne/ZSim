import { useCallback, useEffect, useMemo, useState } from 'react';
import BoxesIcon from '~icons/lucide/boxes';
import GitCompareArrowsIcon from '~icons/lucide/git-compare-arrows';
import NetworkIcon from '~icons/lucide/network';
import RefreshCwIcon from '~icons/lucide/refresh-cw';
import ShieldCheckIcon from '~icons/lucide/shield-check';
import { useLanguage } from '../../hooks/useLanguage';
import { buffGraphClient } from './api/buffGraphClient';
import type {
  BuffGraphMigrationCatalog,
  BuffGraphParityMatrix,
  BuffGraphSpecSummary,
} from './api/buffGraphClient';
import { GraphEditorView } from './views/GraphEditorView';
import { MigrationCatalogView } from './views/MigrationCatalogView';
import { ParityMatrixView } from './views/ParityMatrixView';

type WorkbenchTab = 'editor' | 'catalog' | 'matrix';

type BuffGraphWorkbenchProps = {
  className?: string;
};

const tabConfig: { key: WorkbenchTab; label: string; labelKey?: string; Icon: typeof BoxesIcon }[] = [
  { key: 'editor', label: 'Editor', Icon: NetworkIcon },
  { key: 'catalog', label: 'Block Catalog', labelKey: 'buffGraph.tabs.catalog', Icon: BoxesIcon },
  { key: 'matrix', label: 'Parity Matrix', labelKey: 'buffGraph.tabs.matrix', Icon: GitCompareArrowsIcon },
];

const tabFromHashValue = (hash: string): WorkbenchTab => {
  const [menuKey, tabKey] = hash.replace(/^#/, '').split(':');
  if (menuKey !== 'buff-graph') return 'editor';
  if (tabKey === 'catalog') return 'catalog';
  return tabKey === 'matrix' ? 'matrix' : 'editor';
};

const hashForWorkbenchTab = (tab: WorkbenchTab) =>
  tab === 'editor' ? '#buff-graph' : `#buff-graph:${tab}`;

const initialTab = (): WorkbenchTab => {
  if (typeof window === 'undefined') return 'editor';
  return tabFromHashValue(window.location.hash);
};

export const BuffGraphWorkbench = ({ className = '' }: BuffGraphWorkbenchProps) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<WorkbenchTab>(initialTab);
  const [graphs, setGraphs] = useState<BuffGraphSpecSummary[]>([]);
  const [catalog, setCatalog] = useState<BuffGraphMigrationCatalog>();
  const [matrix, setMatrix] = useState<BuffGraphParityMatrix>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(undefined);
    try {
      const [nextGraphs, nextCatalog, nextMatrix] = await Promise.all([
        buffGraphClient.listGraphs(),
        buffGraphClient.getMigrationCatalog(),
        buffGraphClient.getParityMatrix(),
      ]);
      setGraphs(nextGraphs);
      setCatalog(nextCatalog);
      setMatrix(nextMatrix);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : String(nextError));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    const handleHashChange = () => setActiveTab(tabFromHashValue(window.location.hash));
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const activeGraphs = useMemo(
    () => graphs.filter(graph => graph.runtime_status !== 'visual_graph_disabled'),
    [graphs],
  );

  const activateTab = (tab: WorkbenchTab) => {
    setActiveTab(tab);
    if (typeof window !== 'undefined') {
      window.history.replaceState(null, '', hashForWorkbenchTab(tab));
    }
  };

  return (
    <div
      data-buff-graph-workbench
      className={`flex min-h-0 flex-1 flex-col overflow-hidden px-[24px] pb-[24px] ${className}`}
    >
      <div className="mb-[12px] grid grid-cols-1 gap-[12px] xl:grid-cols-[minmax(0,1fr)_auto]">
        <div className="grid grid-cols-2 gap-[8px] md:grid-cols-4">
          <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
            <div className="flex items-center gap-[6px] text-[11px] uppercase text-[#777]">
              <NetworkIcon className="h-[13px] w-[13px]" />
              Graphs
            </div>
            <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">{graphs.length}</div>
          </div>
          <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
            <div className="text-[11px] uppercase text-[#777]">Active</div>
            <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">
              {activeGraphs.length}
            </div>
          </div>
          <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
            <div className="text-[11px] uppercase text-[#777]">Blocks</div>
            <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">
              {catalog?.blocks.length ?? 0}
            </div>
          </div>
          <div className="rounded-[8px] border border-[#E6E6E6] bg-[#FAFAFA] p-[10px]">
            <div className="flex items-center gap-[6px] text-[11px] uppercase text-[#777]">
              <ShieldCheckIcon className="h-[13px] w-[13px]" />
              Code Nodes
            </div>
            <div className="mt-[4px] text-[22px] leading-[26px] text-[#222]">
              {catalog?.custom_python_nodes_allowed ? 'On' : 'Off'}
            </div>
          </div>
        </div>
        <button
          type="button"
          className="inline-flex h-[36px] shrink-0 items-center gap-[7px] rounded-[8px] bg-[#202020] px-[12px] text-[13px] text-white hover:bg-[#343434] disabled:cursor-not-allowed disabled:opacity-60"
          disabled={loading}
          onClick={() => void refresh()}
        >
          <RefreshCwIcon className="h-[14px] w-[14px]" />
          Refresh
        </button>
      </div>

      <div className="mb-[12px] flex min-h-[36px] shrink-0 gap-[6px] overflow-x-auto border-b border-[#E6E6E6]">
        {tabConfig.map(({ key, label, labelKey, Icon }) => (
          <button
            key={key}
            type="button"
            data-buff-graph-tab={key}
            aria-selected={key === activeTab}
            aria-current={key === activeTab ? 'page' : undefined}
            className={[
              'inline-flex h-[36px] shrink-0 items-center gap-[7px] border-b-2 px-[10px] text-[13px]',
              key === activeTab
                ? 'border-[#F5C542] text-[#6F5700]'
                : 'border-transparent text-[#555] hover:text-[#222]',
            ].join(' ')}
            onClick={() => activateTab(key)}
          >
            <Icon className="h-[14px] w-[14px]" />
            {labelKey ? t(labelKey) : label}
          </button>
        ))}
      </div>

      <div className="min-h-0 flex flex-1 overflow-hidden rounded-[8px] border border-[#E6E6E6]">
        {activeTab === 'editor' ? (
          <GraphEditorView graphs={graphs} catalog={catalog} refresh={refresh} />
        ) : null}
        {activeTab === 'catalog' ? (
          <MigrationCatalogView catalog={catalog} loading={loading} error={error} />
        ) : null}
        {activeTab === 'matrix' ? (
          <ParityMatrixView matrix={matrix} loading={loading} error={error} />
        ) : null}
      </div>
    </div>
  );
};
