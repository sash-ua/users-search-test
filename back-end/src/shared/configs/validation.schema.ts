import * as Joi from 'joi';

export const validationSchema = Joi.object({
    IS_CORS_ENABLED: Joi.boolean().required(),
    APP_NAME: Joi.string().required(),
    APP_ENV: Joi.string().required(),
    APP_PORT: Joi.number().required(),
    PYTHON_BIN: Joi.string().required(),
    PYTHON_SEARCH_MODULE: Joi.string().required(),
    PUBLIC_BACKEND_URL: Joi.string().required(),
    allowUnknown: true
});
