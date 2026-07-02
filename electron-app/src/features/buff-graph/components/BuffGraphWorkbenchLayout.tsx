import type { ReactNode } from 'react';

type BuffGraphWorkbenchLayoutProps = {
  left: ReactNode;
  center: ReactNode;
  right: ReactNode;
};

export const BuffGraphWorkbenchLayout = ({ left, center, right }: BuffGraphWorkbenchLayoutProps) => (
  <div className="buff-graph-editor-grid">
    <aside className="buff-graph-editor-sidebar">{left}</aside>
    <main className="buff-graph-editor-canvas">{center}</main>
    <aside className="buff-graph-editor-inspector">{right}</aside>
  </div>
);
