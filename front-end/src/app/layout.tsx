import type {Metadata} from 'next';
import {Suspense} from 'react';
import {ThemeServerProvider} from '../providers/ThemeServerProvider';
import Loading from '../components/Loading';

export const metadata: Metadata = {
    title: 'Context Users Search',
    description: 'Query your embeddings collection, optionally reindexing with custom chunking parameters.',
};

export default function RootLayout({children}: {children: React.ReactNode}) {
    return (
        <html lang="en">
            <body suppressHydrationWarning>
                <Suspense fallback={<Loading />}>
                    <ThemeServerProvider>{children}</ThemeServerProvider>
                </Suspense>
            </body>
        </html>
    );
}
