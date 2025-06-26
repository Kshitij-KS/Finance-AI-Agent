
#Backend
FROM python:3.9-slim AS backend

WORKDIR /usr/src/app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .env .
COPY backend/ .

#exposing the server on which backend runs
EXPOSE 5000

CMD [ "python", "FinanceAI.py" ]

#Frontend 
FROM node:18-alpine  AS frontend

WORKDIR /usr/src/app

COPY Frontend/package.json .
COPY Frontend/package-lock.json .

# Installing frontend dependencies
RUN npm install

COPY Frontend/ .

EXPOSE 3000

CMD [ "npm", "start" ]

# # #Building frontend
# # RUN npm run build 

# # #using the nginx with the alpine tag [which is a minimal and light weight version of nginx based on Alpine Linux] to serve the image
# # FROM nginx:alpine

# # #copying the built Frontend files to Nginx
# # COPY --from=Frontend /app/build/ usr/share/nginx/html

# # #copying the nginx configuration
# # COPY nginx.config /etc/nginx/conf.d/default.conf

# # #Exposing the port Nginx runs on
# # EXPOSE 80

# # #Command to run nginx
# # CMD [ "nginx", "-g", "daemon off;" ]

