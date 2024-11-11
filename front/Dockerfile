FROM node:18-alpine

WORKDIR /app

COPY ./front/package.json ./front/package-lock.json ./

RUN npm install

COPY . .

EXPOSE 80

CMD [ "npm", "run", "dev" ]