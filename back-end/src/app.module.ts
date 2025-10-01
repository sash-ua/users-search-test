import {Module} from '@nestjs/common';
import {ConfigModule, ConfigService} from '@nestjs/config';
import {SearchModule} from './search/search.module';
import {DatasetsModule} from './datasets/datasets.module';
import {validationSchema} from './shared/configs/validation.schema';
import {APP_CONFIG} from "./shared/constants/app-config-token";
import {configProviderFactory} from "./shared/providers/config-provider";

@Module({
    imports: [
        ConfigModule.forRoot({
            validationSchema,
            isGlobal: true,
            envFilePath: [
                '.env',
                `.env.${process.env.NODE_ENV}`,
            ],
        }),
        SearchModule,
        DatasetsModule,
    ],
    providers: [
        {
            provide: APP_CONFIG,
            inject: [ConfigService],
            useFactory: configProviderFactory,
        },
    ],
    exports: [APP_CONFIG],
})
export class AppModule {
}
