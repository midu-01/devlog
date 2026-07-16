# ---- Stage 1: build the static bundle ----
FROM node:22-slim AS builder

WORKDIR /build
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Stage 2: serve with nginx ----
FROM nginx:1.27-alpine

COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
