import {ConfigService} from "@nestjs/config";

export const configProviderFactory = (cfg: ConfigService) => ({
    name: cfg.get<string>('APP_NAME', 'Search API'),
    env: cfg.get<string>('APP_ENV', (cfg.get('NODE_ENV') as string) || 'development'),
    cors: cfg.get<boolean>('IS_CORS_ENABLED', true),
    port: cfg.get<number>('APP_PORT', 3001),
})