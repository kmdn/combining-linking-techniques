# Install the base requirements for the app.
# This stage is to support development.

# docker-compose up --build --remove-orphans

FROM tomcat:9.0 AS base
#WORKDIR /

# Metadata indicating an image maintainer.
LABEL maintainer="kmdn@github.com"

# Export has to be done through Eclipse, 
# otherwise you also need to get the agnos_collab-0.0.1.jar depedency
# which is annoying/difficult/'impossible' to do due to the WAR's 
# way of deploying in Tomcat
#ADD agnos-web-0.0.1.war /usr/local/tomcat/webapps/
ADD ROOT.war /usr/local/tomcat/webapps/

#ADD agnos_collab-0.0.1.jar /usr/local/tomcat/webapps/ROOT/WEB-INF/lib/
# run program on startup
# CMD ["python", "linker_recommender.py"]
ADD evaluation_datasets/ /usr/local/tomcat/default/resources/data/evaluation_datasets/
ADD other_datasets/* /usr/local/tomcat/default/resources/data/evaluation_datasets/

# Expose port 8080 (can also be done in docker-compose.yml)
EXPOSE 8080
# Run tomcat...
# Foreground
CMD ["catalina.sh", "run"]


# Background w/ logs showing
#CMD ["tomcat/bin/startup.sh"]
#CMD ["tail", "-f", "tomcat/logs/catalina.out"]