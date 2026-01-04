# Runbook: Postgres lento / locks

## Sintomas
- Aumento de latência em endpoints
- Queries travando / tempo de resposta alto

## Hipóteses
- locks em tabelas
- queries sem índice
- autovacuum atrasado
- saturação de IO

## Checklist
1) Identificar queries lentas e locks
2) Verificar índices e plano de execução
3) Checar conexões ativas e pool
4) Inspecionar IO/CPU/RAM

## Comandos read-only (exemplos)
- SELECT now();
- SELECT * FROM pg_stat_activity;
- SELECT * FROM pg_locks;
