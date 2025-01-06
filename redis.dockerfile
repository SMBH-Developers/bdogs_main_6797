FROM redis:latest

# Копируем конфигурационный файл
COPY src/config/redis.conf /usr/local/etc/redis/redis.conf

USER root
RUN mkdir -p /local_storage && \
    chown -R redis:redis /local_storage && \
    chmod -R 777 /local_storage

USER redis

EXPOSE 6380

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
