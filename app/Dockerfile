# syntax=docker/dockerfile:1.4

FROM python:3.11 AS builder

EXPOSE 8000
WORKDIR /app 
COPY requirements.txt /app
RUN python3 -m pip install --upgrade pip
#RUN apt-get update && apt-get install -y \
#    build-essential 
 #   gfortran \
#    liblapack-dev \
#    libstdc++ \
#    musl-dev \
 #   libopenblas-dev

#RUN python3 -m pip install --upgrade Cython


RUN apt-get update

RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app 
ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]


#FROM builder as dev-envs
#RUN <<EOF
#apt-get update
#apt-get install -y git
#EOF

#RUN <<EOF
#addgroup -S docker
#adduser -S --shell /bin/bash --ingroup docker vscode

#EOF
# install Docker tools (cli, buildx, compose)
#COPY --from=gloursdocker/docker / /
#CMD ["manage.py", "runserver", "0.0.0.0:8000"]
