import { Module } from '@nestjs/common';
import { DatasetsController } from './datasets.controller';

@Module({
  controllers: [DatasetsController],
})
export class DatasetsModule {}

