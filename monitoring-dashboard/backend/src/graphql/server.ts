import { ApolloServer } from 'apollo-server-express';
import { buildSchema } from 'type-graphql';
import { TestResolver } from './resolvers/test-resolver';
import { CoverageResolver } from './resolvers/coverage-resolver';
import { MetricsResolver } from './resolvers/metrics-resolver';
import { AlertResolver } from './resolvers/alert-resolver';
import { DashboardResolver } from './resolvers/dashboard-resolver';
import { logger } from '../utils/logger';

export async function createGraphQLServer(): Promise<ApolloServer> {
  try {
    const schema = await buildSchema({
      resolvers: [
        TestResolver,
        CoverageResolver,
        MetricsResolver,
        AlertResolver,
        DashboardResolver
      ],
      dateScalarMode: 'isoDate',
      validate: false
    });

    const server = new ApolloServer({
      schema,
      context: ({ req, res }) => ({
        req,
        res,
        user: req.user // If you have authentication
      }),
      introspection: process.env.NODE_ENV !== 'production',
      playground: process.env.NODE_ENV !== 'production',
      formatError: (error) => {
        logger.error('GraphQL Error:', error);
        return {
          message: error.message,
          code: error.extensions?.code,
          path: error.path,
          timestamp: new Date().toISOString()
        };
      },
      formatResponse: (response, { request }) => {
        logger.debug('GraphQL Response', {
          operationName: request.operationName,
          variables: request.variables
        });
        return response;
      }
    });

    logger.info('GraphQL server created successfully');
    return server;
  } catch (error) {
    logger.error('Failed to create GraphQL server:', error);
    throw error;
  }
}

// Export server instance
export const graphqlServer = createGraphQLServer();