# Tech Stack → enableXXX Mapping Rules

## Principles
- Conservative enabling: only enable when the keyword is explicit.
- Prefer explicit user switches when provided (e.g., user says "enableMysqlConnectorJ").
- If user says "redis" but doesn't say "redisson", do NOT auto-enable redisson by default.

## High-confidence keyword mapping (examples)
### DB
- mysql → enableMysqlConnectorJ
- postgresql/postgres → enablePostgresql
- oracle/ojdbc → enableOjdbc11
- sqlite → enableSqliteJdbc
- sql server/mssql → enableMssqlJdbc
- db2 → enableDb2jcc
- kingbase → enableKingbase8
- vastbase → enableVastbaseJdbc
- oceanbase → enableOceanbaseClient
- duckdb → enableDuckdbJdbc
- 达梦/dameng → enableDmJdbcDriver18
- sybase/jconn4 → enableJconn4
- access/ucanaccess → enableUcanaccess

### Connection pool
- hikari/hikaricp → enableHikariCP
- druid → enableDruid

### Cache
- redisson → enableRedissonSpringBootStarter
- caffeine → enableCaffeine

### MQ / Streaming
- kafka → enableKafkaClients
- rocketmq → enableRocketmqClient

### JSON / Jackson
- jsr310/java time/localdatetime → enableJacksonDatatypeJsr310
- jdk8 → enableJacksonDatatypeJdk8
- afterburner → enableJacksonModuleAfterburner

### Build-time helpers
- lombok → enableLombok
- mapstruct → enableMapstruct + enableMapstructProcessor
- lombok + mapstruct → also enableLombokMapstructBinding

### Storage / HTTP
- okhttp → enableOkhttpJvm
- minio → enableMinio
- aws s3 / s3 → enableAwsS3
- transfer manager → enableAwsS3TransferManager
- huawei obs / obs → enableEsdkObsJavaBundle

### Utilities
- commons-lang3 → enableCommonsLang3
- commons-io → enableCommonsIo
- guava → enableGuava

### Security
- nimbus/jose/jwt → enableNimbusJoseJwt
- auth0/java-jwt → enableJavaJwt

### ZK / Curator
- zookeeper → enableZookeeper
- curator → enableCuratorClient + enableCuratorRecipes

### Spring AI MCP
- mcp → enableSpringAiStdioMcpServer
- mcp + webmvc → enableSpringAiSSEMvcMcpServer
- mcp + mvc → enableSpringAiSSEMvcMcpServer
- mcp + webflux → enableSpringAiSSEWebFluxMcpServer + enableSpringAiMcpClient

## When in doubt
Do not enable. Ask the user to confirm or require explicit --enable flags.
