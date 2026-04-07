FROM nginx:alpine

# Remove the default nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config file 
# (Path relative to the build context)
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend files to nginx html folder 
# (Paths relative to the build context)
COPY frontend/index.html /usr/share/nginx/html/index.html
COPY frontend/style.css /usr/share/nginx/html/style.css
COPY frontend/app.js /usr/share/nginx/html/app.js

EXPOSE 80