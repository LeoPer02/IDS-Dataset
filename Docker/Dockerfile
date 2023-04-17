FROM ubuntu:18.04

# Turn off some questions asked during installation, to avoid infinte stall
ARG DEBIAN_FRONTEND=noninteractive

# Update system
RUN apt-get update -y &&\
    apt-get install php -y &&\
    apt-get install apache2 -y &&\
    apt-get install php-mysql -y

RUN rm -f /var/www/html/index.html



# Install BCC dependencies
RUN apt-get -y install bison build-essential cmake flex git libedit-dev \
  libllvm6.0 llvm-6.0-dev libclang-6.0-dev python zlib1g-dev libelf-dev libfl-dev python3-distutils

# Change Work Directory
WORKDIR /

RUN dpkg-reconfigure dash

# Download and Install BCC
# It uses bash because of pushd and popd
RUN bash -xc "\
git clone https://github.com/iovisor/bcc.git --branch v0.24.0; \
mkdir bcc/build; \ 
cd bcc/build; \
cmake ..; \
make; \
make install; \
cmake -DPYTHON_CMD=python3 ..; \
pushd src/python/; \
make; \
make install; \
popd; \
"

WORKDIR /

##################################################
#                                                #   
#                                                #
#            SYSCALL TRACING AFONSO              #
#         (Confirmar se posso publicar)          #
#                                                #
#                                                #
##################################################

RUN git clone https://github.com/fonsow/ebriareospf.git

CMD ["apache2ctl", "-D", "FOREGROUND"]