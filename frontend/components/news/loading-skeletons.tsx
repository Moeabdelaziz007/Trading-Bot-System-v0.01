import { motion } from 'framer-motion';

// Briefing skeleton component
export function BriefingSkeleton() {
    return (
        <div className="relative p-6 rounded-xl border border-gray-800 bg-gray-900/50">
            <div className="relative z-10">
                {/* Header skeleton */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-5 h-5 bg-gray-700 rounded animate-pulse" />
                        <div className="w-32 h-4 bg-gray-700 rounded animate-pulse" />
                    </div>
                    <div className="w-20 h-8 bg-gray-700 rounded-full animate-pulse" />
                </div>

                {/* Content skeleton */}
                <div className="min-h-[80px] space-y-2">
                    <div className="h-4 bg-gray-700 rounded animate-pulse" />
                    <div className="h-4 bg-gray-700 rounded animate-pulse w-5/6" />
                    <div className="h-4 bg-gray-700 rounded animate-pulse w-4/6" />
                </div>

                {/* Tags skeleton */}
                <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-800">
                    <div className="w-20 h-4 bg-gray-700 rounded animate-pulse" />
                    <div className="w-16 h-6 bg-gray-700 rounded animate-pulse" />
                    <div className="w-20 h-6 bg-gray-700 rounded animate-pulse" />
                    <div className="w-18 h-6 bg-gray-700 rounded animate-pulse" />
                </div>
            </div>
        </div>
    );
}

// News item skeleton component
export function NewsItemSkeleton() {
    return (
        <motion.div
            className="block p-4 md:p-6 rounded-xl border border-gray-800 bg-gray-900/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="flex justify-between items-start mb-3">
                <div className="w-16 h-4 bg-gray-700 rounded animate-pulse" />
                <div className="w-12 h-3 bg-gray-700 rounded animate-pulse" />
            </div>
            
            <div className="space-y-2 mb-3">
                <div className="h-4 bg-gray-700 rounded animate-pulse" />
                <div className="h-4 bg-gray-700 rounded animate-pulse w-5/6" />
            </div>
            
            <div className="flex justify-end">
                <div className="w-4 h-4 bg-gray-700 rounded animate-pulse" />
            </div>
        </motion.div>
    );
}

// News grid skeleton component
export function NewsGridSkeleton({ count = 4 }: { count?: number }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {Array.from({ length: count }).map((_, index) => (
                <NewsItemSkeleton key={index} />
            ))}
        </div>
    );
}

// Error component for data fetching
export function DataFetchError({ 
    message = "Failed to load data", 
    onRetry 
}: { 
    message?: string; 
    onRetry?: () => void;
}) {
    return (
        <div className="flex flex-col items-center justify-center p-8 rounded-xl border border-red-500/20 bg-red-500/5">
            <div className="text-red-400 text-center mb-4">
                <p className="text-lg font-medium">{message}</p>
                <p className="text-sm mt-2 opacity-75">Please check your connection and try again</p>
            </div>
            {onRetry && (
                <motion.button
                    onClick={onRetry}
                    className="px-4 py-2 rounded-lg text-sm flex items-center gap-2 transition-all border border-red-500/30 bg-red-500/10 text-red-400"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Retry
                </motion.button>
            )}
        </div>
    );
}