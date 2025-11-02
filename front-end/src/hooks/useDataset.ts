import {useState, useEffect, ChangeEvent} from 'react';

export function useDataset(BACKEND_URL: string) {
    const [dataset, setDataset] = useState<string>('');
    const [datasets, setDatasets] = useState<string[]>([]);
    const [file, setFile] = useState<File | null>(null);
    const [uploadName, setUploadName] = useState<string>('data.json');

    useEffect(() => {
        fetch(`${BACKEND_URL}/datasets`).then(async (response) => {
            try {
                if (!response.ok) {
                    setDatasets([]);
                    return;
                }
                const data = await response.json();
                setDatasets(Array.isArray((data as any).files) ? (data as any).files : []);
            } catch {
                setDatasets([]);
            }
        }).catch(() => setDatasets([]));
    }, [BACKEND_URL]);

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        const nextFile = event.target.files?.[0] ?? null;
        setFile(nextFile);
        if (nextFile) {
            setDataset('');
            setUploadName(nextFile.name ?? 'data.json');
        } else {
            setUploadName('data.json');
        }
        event.target.value = '';
    };

    const handleUpload = async (): Promise<string | null> => {
        if (!file) return dataset || null;
        const fd = new FormData();
        fd.append('file', file);
        if (uploadName && uploadName.trim()) fd.append('name', uploadName.trim());
        const res = await fetch(`${BACKEND_URL}/datasets`, {method: 'POST', body: fd});
        if (!res.ok) {
            let msg: string | undefined;
            try {
                const j = await res.clone().json();
                msg = (j as any)?.error || (j as any)?.message;
            } catch {}
            const text = await res.text().catch(() => '');
            throw new Error(msg || text || 'Upload failed');
        }
        try {
            const body = await res.json();
            return (body as any).path as string;
        } catch {
            throw new Error('Upload failed: invalid response');
        }
    };

    return {
        dataset,
        setDataset,
        datasets,
        file,
        setFile,
        uploadName,
        setUploadName,
        handleFileChange,
        handleUpload,
    };
}
