FROM redis:latest

# Копируем конфигурационный файл
COPY src/config/redis.conf /usr/local/etc/redis/redis.conf

# Указываем права на конфиг и директорию
RUN chown redis:redis /usr/local/etc/redis/redis.conf && \
    chmod 777 /local_storage

# Открываем стандартный порт Redis
EXPOSE 6380

# Запускаем Redis с нашим конфигом
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
