# from django.core.cache import cache
# from django_redis import get_redis_connection
# from rest_framework_simplejwt.tokens import RefreshToken
import redis

client = redis.Redis(host='localhost', port=6379, db=0)

# Доступ до нашого Redis-кешу
# redis_cache = get_redis_connection("refresh_token_cache")
# cache['refresh_token_cache']

def store_refresh_token(user_id, refresh_token, expiration_time):
    # Зберігаємо рефреш-токен у Redis з терміном дії
    # redis_cache.set(f'refresh_token:{user_id}', refresh_token, timeout=expiration_time)
    print(f'{user_id} : {refresh_token}')
    try:
        # Set a key-value pair in Redis
            # client.set('test_key', 'test_value')
            client.set(f'refresh_token:{user_id}', refresh_token, timeout=expiration_time)
        
        # Get the value from Redis
            # value = client.get('test_key')
        
        # Decode the value to a string, as Redis returns bytes
            # if value:
            #     value = value.decode('utf-8')
        
        # Return the value in the HTTP response
            # print({"message": "Success", "value": value})
    
    except redis.exceptions.ConnectionError as e:
        return {"error": "Redis connection error", "details": str(e)}
    
    except Exception as e:
        return {"error": "An unexpected error occurred", "details": str(e)}
    



def delete_refresh_token(user_id):
    # Видаляємо рефреш-токен з Redis
    # redis_cache.delete(f'refresh_token:{user_id}')
    client.delete(f'refresh_token:{user_id}')

def is_refresh_token_valid(user_id, refresh_token):
    # Перевіряємо, чи дійсний токен у Redis
    # cached_token = redis_cache.get(f'refresh_token:{user_id}')
    cached_token = client.get(f'refresh_token:{user_id}')
    return cached_token == refresh_token
