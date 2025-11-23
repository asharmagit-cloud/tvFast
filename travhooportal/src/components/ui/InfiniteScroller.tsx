import React, { useEffect, useRef, useCallback } from 'react';

interface InfiniteScrollerProps<T> {
  items: T[];
  batch: number;
  loadMoreBufferDistance?: number;
  virtualizationTriggerDistance?: number;
  loadMore: () => void;
  wrapperClassName?: string;
  loader?: React.ReactNode;
  hasMore: boolean;
  renderItem: (item: T, index: number) => React.ReactNode;
}

function InfiniteScroller<T>({
  items,
  batch,
  loadMoreBufferDistance = 300,
  virtualizationTriggerDistance = 1000,
  loadMore,
  wrapperClassName = '',
  loader = null,
  hasMore,
  renderItem,
}: InfiniteScrollerProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Infinite scroll handler
  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    if (
      hasMore &&
      scrollHeight - scrollTop - clientHeight <= loadMoreBufferDistance
    ) {
      loadMore();
    }
  }, [hasMore, loadMore, loadMoreBufferDistance]);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;
    node.addEventListener('scroll', handleScroll);
    return () => {
      node.removeEventListener('scroll', handleScroll);
    };
  }, [handleScroll]);

  // Simple virtualization: only render items within virtualizationTriggerDistance of viewport
  const [startIdx, setStartIdx] = React.useState(0);
  const [endIdx, setEndIdx] = React.useState(batch);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;

    const onScroll = () => {
      const scrollTop = node.scrollTop;
      const itemHeight = node.scrollHeight / Math.max(items.length, 1);
      const visibleCount = Math.ceil(
        node.clientHeight / Math.max(itemHeight, 1),
      );
      const buffer = Math.ceil(
        virtualizationTriggerDistance / Math.max(itemHeight, 1),
      );
      const firstVisible = Math.floor(scrollTop / Math.max(itemHeight, 1));
      setStartIdx(Math.max(0, firstVisible - buffer));
      setEndIdx(Math.min(items.length, firstVisible + visibleCount + buffer));
    };

    node.addEventListener('scroll', onScroll);
    onScroll(); // initialize
    return () => {
      node.removeEventListener('scroll', onScroll);
    };
  }, [items.length, virtualizationTriggerDistance]);

  const visibleItems = items.slice(startIdx, endIdx);

  return (
    <div ref={containerRef} style={{ overflowY: 'auto', height: '100%' }}>
      <div style={{ height: startIdx * 1, pointerEvents: 'none' }} />
      <div className={wrapperClassName}>
        {visibleItems.map((item, idx) => renderItem(item, startIdx + idx))}
      </div>
      <div
        style={{ height: (items.length - endIdx) * 1, pointerEvents: 'none' }}
      />
      {hasMore && loader}
    </div>
  );
}

export default InfiniteScroller;
