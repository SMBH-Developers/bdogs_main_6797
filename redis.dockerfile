FROM redis:latest

# Копируем конфигурационный файл
COPY src/config/redis.conf /usr/local/etc/redis/redis.conf

# Переключаемся на пользователя redis
USER redis

# Создаем директорию и устанавливаем права
RUN mkdir -p /local_storage && \
    chown -R redis:redis /local_storage /usr/local/etc/redis/redis.conf && \
    chmod -R 755 /local_storage

    # Если не отрабатывает, то можно попробовать так:
# sudo chown -R 999:999 ./local_storage
# sudo chmod -R 777 ./local_storage

# Открываем порт Redis
EXPOSE 6380

# Запускаем Redis с нашим конфигом
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
