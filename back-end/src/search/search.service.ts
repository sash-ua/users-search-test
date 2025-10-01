import { Injectable } from '@nestjs/common';
import { runPythonQuery } from './python';
import {SearchQueryArgs} from "../shared/models/search-query-args.model";
import {ConfigService} from "@nestjs/config";

@Injectable()
export class SearchService {
  constructor(private readonly configService: ConfigService) {}

  async query(args: SearchQueryArgs) {
    return await runPythonQuery(args, this.configService);
  }
}

