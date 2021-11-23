# Install the base requirements for the app.
# This stage is to support development.
FROM tomcat:9.0 AS base
#WORKDIR /

# Metadata indicating an image maintainer.
LABEL maintainer="kmdn@github.com"

ADD agnos-web-0.0.1.war /usr/local/tomcat/webapps/

# run program on startup
# CMD ["python", "linker_recommender.py"]

# Expose port 8080 (can also be done in docker-compose.yml)
EXPOSE 8080
# Run tomcat...
CMD ["catalina.sh", "run"]
