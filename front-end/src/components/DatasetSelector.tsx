'use client';

import {ChangeEvent} from 'react';
import {
    Button,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    TextField,
    Typography,
} from '@mui/material';
import type {SelectChangeEvent} from '@mui/material/Select';

type DatasetSelectorProps = {
    dataset: string;
    setDataset: (value: string) => void;
    datasets: string[];
    file: File | null;
    handleFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
    uploadName: string;
    setUploadName: (value: string) => void;
};

export function DatasetSelector({
    dataset,
    setDataset,
    datasets,
    file,
    handleFileChange,
    uploadName,
    setUploadName,
}: DatasetSelectorProps) {
    const handleDatasetChange = (event: SelectChangeEvent<string>) => {
        const value = event.target.value;
        setDataset(value);
    };

    return (
        <Stack spacing={2}>
            <FormControl fullWidth disabled={datasets.length === 0}>
                <InputLabel id="dataset-select-label">Existing dataset</InputLabel>
                <Select
                    labelId="dataset-select-label"
                    value={dataset}
                    label="Existing dataset"
                    onChange={handleDatasetChange}
                >
                    <MenuItem value="">
                        <em>None</em>
                    </MenuItem>
                    {datasets.map((name) => (
                        <MenuItem key={name} value={name}>
                            {name}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            <Stack spacing={1.5}>
                <Typography variant="subtitle1" fontWeight={600}>
                    Or upload JSON
                </Typography>
                <Stack direction={{xs: 'column', sm: 'row'}} spacing={2} alignItems={{sm: 'center'}}>
                    <Button variant="outlined" component="label">
                        {file ? 'Replace JSON file' : 'Choose JSON file'}
                        <input hidden type="file" accept="application/json" onChange={handleFileChange} />
                    </Button>
                    <Typography variant="body2" color="text.secondary">
                        {file ? file.name : 'No file selected'}
                    </Typography>
                </Stack>
                <TextField
                    id="upload-name"
                    name="uploadName"
                    label="Upload name"
                    value={uploadName}
                    onChange={(event) => setUploadName(event.target.value)}
                    helperText="Optional override for the stored filename"
                    autoComplete="off"
                    spellCheck={false}
                    inputProps={{'data-gramm': 'false', 'data-enable-grammarly': 'false'}}
                    disabled={!file}
                />
            </Stack>
        </Stack>
    );
}
