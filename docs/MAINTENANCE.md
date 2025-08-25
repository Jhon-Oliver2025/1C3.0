# Guia de Manutenção - 1Crypten

## 🔄 Atualizações

### Deploy de nova versão
```bash
# Pull das mudanças
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### Rollback
```bash
# Voltar para versão anterior
git checkout <commit-anterior>
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

## 🗄️ Backup

### Backup do banco de dados
```bash
# Backup automático diário configurado
# Backup manual:
docker exec <container-db> pg_dump -U user database > backup.sql
```

### Backup de arquivos
```bash
# Backup de uploads e configurações
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ config/
```

## 📊 Monitoramento

### Logs importantes
- Aplicação: `docker-compose logs app`
- Banco: `docker-compose logs db`
- Nginx: `docker-compose logs nginx`

### Métricas
- CPU e memória: `docker stats`
- Espaço em disco: `df -h`
- Conexões: `netstat -an | grep :80`

## 🚨 Troubleshooting

### Problemas comuns
1. **Container não inicia**: Verificar logs e variáveis de ambiente
2. **Erro 502**: Verificar se app está rodando na porta correta
3. **Lentidão**: Verificar uso de CPU/memória

### Comandos úteis
```bash
# Restart completo
docker-compose -f docker-compose.production.yml restart

# Limpar cache
docker system prune -f

# Verificar saúde
curl -f http://localhost/api/health
```
