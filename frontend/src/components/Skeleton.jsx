import React from 'react';

export const Skeleton = ({ className = '', style }) => (
  <div
    className={`rounded bg-gray-200 animate-shimmer ${className}`}
    style={{
      backgroundImage: 'linear-gradient(90deg, rgba(0,0,0,0.06) 0%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.06) 100%)',
      backgroundSize: '200% 100%',
      ...style,
    }}
  />
);

export const CardSkeleton = () => (
  <div className="card animate-fade-in">
    <Skeleton className="h-5 w-1/2 mb-4" />
    <Skeleton className="h-4 w-full mb-2" />
    <Skeleton className="h-4 w-5/6 mb-6" />
    <div className="flex gap-2">
      <Skeleton className="h-9 w-28" />
      <Skeleton className="h-9 w-24" />
    </div>
  </div>
);

export const TableRowSkeleton = () => (
  <div className="flex items-center w-full py-3 px-2">
    <Skeleton className="h-4 w-2/5 mr-3" />
    <Skeleton className="h-4 w-2/5 mr-3" />
    <Skeleton className="h-4 w-1/6" />
  </div>
);

export const LinesSkeleton = ({ lines = 4 }) => (
  <div className="space-y-2">
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton key={i} className="h-4 w-full" style={{ animationDelay: `${i * 100}ms` }} />
    ))}
  </div>
);
