# Runbook: Nginx 502 Bad Gateway

## Sintomas
- Usuários recebem 502 no gateway
- Acontece principalmente em rotas específicas

## Hipóteses comuns
- upstream (app) down / crash
- timeout entre nginx e upstream
- socket/porta incorreta
- limite de conexões no upstream

## Checklist
1) Verificar health do upstream (container/process)
2) Checar logs do nginx (errors)
3) Validar config de upstream/porta
4) Verificar timeouts (proxy_read_timeout)
5) Checar saturação (CPU/RAM) do upstream

## Comandos read-only sugeridos
- docker ps
- docker logs <container>
- journalctl -u nginx --since "10 min ago"
- curl -v http://<upstream>:<port>/health
