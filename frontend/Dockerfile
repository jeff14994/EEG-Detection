FROM nginx:alpine

# Copy all static files to Nginx's default web root
COPY . /usr/share/nginx/html/

# Copy custom Nginx configuration if you have one
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 