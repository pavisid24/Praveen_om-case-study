import { resolve as resolvePath } from 'path';
import { promises as fs } from 'fs';

import {
  coreServices,
  createBackendModule,
} from '@backstage/backend-plugin-api';

import {
  createTemplateAction,
  scaffolderActionsExtensionPoint,
} from '@backstage/plugin-scaffolder-node';

export const scaffolderModuleCustomActions = createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'custom-actions',

  register(reg) {
    reg.registerInit({
      deps: {
        logger: coreServices.logger,
        scaffolder: scaffolderActionsExtensionPoint,
      },

      async init({ logger, scaffolder }) {
        scaffolder.addActions(
          createTemplateAction({
            id: 'my:custom:action',

            schema: {
              input: z =>
                z.object({
                  message: z.string().optional(),
                }),
            },

            async handler(ctx) {
              const filePath = resolvePath(
                ctx.workspacePath,
                'custom-file.txt',
              );

              await fs.writeFile(
                filePath,
                ctx.input.message ??
                  'This file was created by my:custom:action',
                'utf8',
              );

              logger.info(`Created ${filePath}`);
            },
          }),
        );
      },
    });
  },
});