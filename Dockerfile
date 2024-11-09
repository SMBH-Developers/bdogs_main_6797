FROM redis:latest

# Копируем конфигурационный файл
COPY src/config/redis.conf /usr/local/etc/redis/redis.conf

# Указываем права только на конфиг
RUN chown redis:redis /usr/local/etc/redis/redis.conf

# Открываем порт Redis
EXPOSE 6380

# Переключаемся на пользователя redis
USER redis

# Запускаем Redis с нашим конфигом
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
