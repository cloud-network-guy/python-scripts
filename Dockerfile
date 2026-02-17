FROM ubuntu:noble
ARG DEBIAN_FRONTEND=noninteractive
ARG HOSTNAME="ubuntu"
ARG PACKAGES="sudo curl wget git nano openssh-server lsb-release gnupg nfs-common"
ARG USERNAME="admin"
WORKDIR /tmp
RUN apt update && apt upgrade -y && apt install -y $PACKAGES && apt clean
# Install python
COPY ./pyproject.toml ./
RUN apt install -y curl python3-full python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install . --break-system-packages
# Setup user account
#RUN echo '${HOSTNAME}' > /etc/hostname
RUN useradd -m -s /bin/bash $USERNAME
RUN usermod -aG sudo $USERNAME
RUN echo $USERNAME:password | chpasswd -c MD5
USER $USERNAME
# Copy Python and Yaml files to home directory
COPY *.py /home/${USERNAME}/
COPY *.yaml /home/${USERNAME}/
# Install ClaudeCode
RUN curl -fsSL https://claude.ai/install.sh | bash
# Setup SSH Server
RUN ssh-keygen -A
RUN mkdir /home/${USERNAME}/.ssh
COPY id_* /home/${USERNAME}/.ssh/
CMD chmod 600 /home/${USERNAME}/.ssh/id_*
#COPY authorized_keys /home/${USERNAME}/.ssh/
#CMD ["pip", "list"]
USER root
RUN mkdir /var/run/sshd
CMD 755 /var/run/sshd
# Enable Password-based SSH Logins
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
CMD ["/usr/sbin/sshd", "-D"]
EXPOSE 22/tcp
