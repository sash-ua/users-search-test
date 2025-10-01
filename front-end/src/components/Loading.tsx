export default function Loading() {
    return (
        <div className="fixed inset-0 flex items-center justify-center bg-background">
            <div className="flex flex-col items-center gap-4">
                <div className="relative w-16 h-16">
                    <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                </div>
                <p className="text-sm text-muted-foreground animate-pulse">Loading...</p>
            </div>
        </div>
    );
}