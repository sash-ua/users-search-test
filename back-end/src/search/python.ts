import {spawn} from 'child_process';
import * as path from 'path';
import {SearchQueryArgs} from "../shared/models/search-query-args.model";
import {ConfigService} from "@nestjs/config";

export function runPythonQuery(args: SearchQueryArgs, configService: ConfigService): Promise<any> {
  const pythonBin = configService.get('PYTHON_BIN');
  const moduleName = configService.get('PYTHON_SEARCH_MODULE');

  const argv: string[] = ['-m', moduleName];
  const dataPath = args.data ?? 'data.json';
  argv.push('--data', dataPath);
  if (args.persist) argv.push('--persist', args.persist);
  if (args.collection) argv.push('--collection', args.collection);
  if (args.space) argv.push('--space', args.space);
  if (args.model) argv.push('--model', args.model);
  if (args.query) argv.push('--query', args.query);
  if (args.k != null) argv.push('--k', String(args.k));
  if (args.threshold != null) argv.push('--threshold', String(args.threshold));
  if (args.normalize) argv.push('--normalize');
  if (args.phrase_prefilter) argv.push('--phrase-prefilter');
  if (args.index_chunks) argv.push('--index-chunks');
  if (args.chunking_mode) argv.push('--chunking-mode', args.chunking_mode);
  if (args.sentences_per_chunk != null) argv.push('--sentences-per-chunk', String(args.sentences_per_chunk));
  if (args.sentence_overlap != null) argv.push('--sentence-overlap', String(args.sentence_overlap));
  if (args.tokens_per_chunk != null) argv.push('--tokens-per-chunk', String(args.tokens_per_chunk));
  if (args.token_overlap != null) argv.push('--token-overlap', String(args.token_overlap));
  if (args.chunk_query_multiplier != null) argv.push('--chunk-query-multiplier', String(args.chunk_query_multiplier));

  const workdir = process.env.PYTHON_WORKDIR || path.resolve(process.cwd(), '..');
  return new Promise((resolve, reject) => {
    const child = spawn(pythonBin, argv, {
      cwd: workdir,
      env: process.env,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let out = '';
    let err = '';
    child.stdout.on('data', (d) => (out += d.toString()));
    child.stderr.on('data', (d) => (err += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(`Python exited ${code}: ${err || out}`));
      }
      try {
        const json = JSON.parse(out.trim());
        resolve(json);
      } catch (e) {
        reject(new Error(`Failed to parse JSON from Python. stderr=${err}, stdout=${out}`));
      }
    });
    child.on('error', reject);
  });
}
