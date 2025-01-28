FROM redis:latest

# делаем один раз
# COPY src/config/dump.rdb /data/dump.rdb 
COPY src/config/redis.conf /usr/local/etc/redis/redis.conf

USER redis

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
