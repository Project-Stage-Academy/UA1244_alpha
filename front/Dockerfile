# Етап побудови
FROM node:18.13.0-alpine

# Встановлення робочої директорії
WORKDIR /app

# Копіюємо тільки package.json та package-lock.json для встановлення залежностей
COPY ./front/package.json ./front/package-lock.json ./

# Встановлюємо залежності
RUN npm install

# Копіюємо весь код з front/
COPY ./front /app

# Будуємо проект
CMD [ "npm", "run", "dev" ]