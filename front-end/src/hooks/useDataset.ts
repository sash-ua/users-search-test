import {useState, useEffect, ChangeEvent} from 'react';

export function useDataset(BACKEND_URL: string) {
    const [dataset, setDataset] = useState<string>('');
    const [datasets, setDatasets] = useState<string[]>([]);
    const [file, setFile] = useState<File | null>(null);
    const [uploadName, setUploadName] = useState<string>('data.json');

    useEffect(() => {
        fetch(`${BACKEND_URL}/datasets`).then(async (response) => {
            try {
                const data = await response.json();
                setDatasets(Array.isArray(data.files) ? data.files : []);
            } catch {
                setDatasets([]);
            }
        });
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
        if (!res.ok) throw new Error('Upload failed');
        const body = await res.json();
        return body.path as string;
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
