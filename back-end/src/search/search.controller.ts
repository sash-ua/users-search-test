import { Body, Controller, Post } from '@nestjs/common';
import { SearchService } from './search.service';

@Controller('search')
export class SearchController {
  constructor(private readonly service: SearchService) {}

  @Post()
  async search(@Body() body: any) {
    const {
      query,
      k,
      normalize,
      phrase_prefilter,
      threshold,
      model,
      data,
      persist,
      collection,
      space,
      index_chunks,
      sentences_per_chunk,
      sentence_overlap,
      chunking_mode,
      tokens_per_chunk,
      token_overlap,
      chunk_query_multiplier,
    } = body || {};

    if (!query || typeof query !== 'string') {
      return { error: 'Body must include query: string' };
    }
    const res = await this.service.query({
      query,
      k,
      normalize,
      phrase_prefilter,
      threshold,
      model,
      data,
      persist,
      collection,
      space,
      index_chunks,
      sentences_per_chunk,
      sentence_overlap,
      chunking_mode,
      tokens_per_chunk,
      token_overlap,
      chunk_query_multiplier,
    });
    return res;
  }
}
