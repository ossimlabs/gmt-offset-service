FROM python:3.8.2-slim
RUN adduser -D -h $HOME -s /sbin/nologin -u 1001 omar \
    && chown 1001:0 -R $HOME
USER 1001
RUN pip3 install pyshp shapely django
ADD ne_10m_time_zones home/ne_10m_time_zones
ADD time_service home/time_service
EXPOSE 8080
WORKDIR /home/time_service
USER 1001
CMD [ "python", "./manage.py", "runserver", "8080" ]
