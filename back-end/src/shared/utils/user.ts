import Ajv from 'ajv';
import * as path from 'path';
import * as fs from 'fs';
import type userSchemaJson from '../../../../schemas/user.schema.json';
import {FromExtendedSchema} from 'json-schema-to-ts';

// Type-only import for compile-time TS type
export type User = FromExtendedSchema<typeof userSchemaJson, any>;

// Resolve JSON Schema at runtime from common locations (or override via USER_SCHEMA_PATH)
function resolveSchemaPath(): string {
    const candidates = [
        process.env.USER_SCHEMA_PATH,
        path.resolve(process.cwd(), '..', 'schemas', 'user.schema.json'),
        path.resolve(process.cwd(), 'schemas', 'user.schema.json'),
    ].filter(Boolean) as string[];
    for (const p of candidates) {
        try {
            if (fs.existsSync(p)) return p;
        } catch {
        }
    }
    throw new Error(
        `User schema not found. Set USER_SCHEMA_PATH or place user.schema.json under ./schemas or ./search/schemas.`
    );
}

const schemaPath = resolveSchemaPath();
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'));

const ajv = new Ajv({allErrors: true, strict: false});

export const validateUser = ajv.compile(schema as any);

export function validateUsersArray(payload: unknown): { valid: boolean; errors?: any[] } {
    if (!Array.isArray(payload)) return {valid: false, errors: [{message: 'Expected array of users'}]};
    for (const [idx, item] of payload.entries()) {
        const ok = validateUser(item as any);
        if (!ok) return {valid: false, errors: (validateUser.errors || []).map(e => ({index: idx, ...e}))};
    }
    return {valid: true};
}

export const userSchema = schema;
