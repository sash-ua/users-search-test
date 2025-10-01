import type {Metadata} from 'next';
import {Suspense} from 'react';
import {ThemeProvider} from '../providers/ThemeProvider';
import Loading from '../components/Loading';

export const metadata: Metadata = {
    title: 'Context Users Search',
    description: 'Query your embeddings collection, optionally reindexing with custom chunking parameters.',
};

export default function RootLayout({children}: {children: React.ReactNode}) {
    return (
        <html lang="en">
            <body>
                <Suspense fallback={<Loading />}>
                    <ThemeProvider>{children}</ThemeProvider>
                </Suspense>
            </body>
        </html>
    );
}
