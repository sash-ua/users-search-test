import {NestFactory} from '@nestjs/core';

import {AppModule} from './app.module';
import type {AppConfig} from './shared/models/app-config.model';
import {APP_CONFIG} from "./shared/constants/app-config-token";

async function bootstrap() {
    const app = await NestFactory.create(AppModule);
    const appConfig = app.get<AppConfig>(APP_CONFIG);

    if (appConfig?.cors) {
        app.enableCors();
    }
    const port = appConfig.port || 3001;
    await app.listen(port);
}

bootstrap();
