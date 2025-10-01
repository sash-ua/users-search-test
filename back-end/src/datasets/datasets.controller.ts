import { Controller, Post, UseInterceptors, UploadedFile, Body, Get } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import * as path from 'path';
import * as fs from 'fs/promises';
import { validateUsersArray } from '../shared/utils/user';

@Controller('datasets')
export class DatasetsController {
  @Post()
  @UseInterceptors(FileInterceptor('file'))
  async upload(
    @UploadedFile() file?: Express.Multer.File,
    @Body('name') name?: string,
    @Body('validate') validate?: string,
  ) {
    const uploadsDir = process.env.DATASETS_DIR || path.resolve(process.cwd(), '..', 'search', 'uploads');
    await fs.mkdir(uploadsDir, { recursive: true });
    if (!file) {
      return { error: 'No file provided. Use multipart/form-data with field "file".' };
    }
    const safeName = (name && String(name).trim()) || file.originalname || 'data.json';
    // Optional: validate JSON array of users against schema before saving
    if (validate && file.mimetype === 'application/json') {
      try {
        const text = file.buffer.toString('utf-8');
        const data = JSON.parse(text);
        const res = validateUsersArray(data);
        if (!res.valid) {
          return { error: 'Invalid dataset format', details: res.errors };
        }
      } catch (e: any) {
        return { error: 'Invalid JSON file', details: e?.message };
      }
    }
    const timestamp = Date.now();
    const destRel = path.join('search', 'uploads', `${timestamp}_${safeName}`);
    const destAbs = path.resolve(process.cwd(), '..', destRel);
    await fs.writeFile(destAbs, file.buffer);
    return { path: destRel };
  }

  @Get()
  async list() {
    const uploadsDir = process.env.DATASETS_DIR || path.resolve(process.cwd(), '..', 'search', 'uploads');
    try {
      const items = await fs.readdir(uploadsDir);
      const files = items.filter((f) => f.endsWith('.json'));
      return { files: files.map((f) => path.join('search', 'uploads', f)) };
    } catch {
      return { files: [] };
    }
  }
}
