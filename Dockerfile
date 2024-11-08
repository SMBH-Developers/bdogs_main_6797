FROM redis:latest

# Копируем конфигурационный файл
COPY src/config/redis.conf /usr/local/etc/redis/redis.conf

# Указываем права на конфиг
RUN chown redis:redis /usr/local/etc/redis/redis.conf

# Открываем стандартный порт Redis
EXPOSE 6379

# Запускаем Redis с нашим конфигом
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
