FROM ubuntu:latest

# Keep apt from prompting for input
ENV UBUNTU_FRONTEND=noninteractive

# Base tooling + HPC/benchmark stack + SSH
RUN apt-get update && apt-get install -y \
    sudo \
    vim \
    wget \
    unzip \
    rsync \
    iputils-ping \
    netcat-openbsd \
    openssh-server \
    iozone3 \
    sysbench \
    stress-ng \
    iperf3 \
    hpcc \
    mpich \
    openmpi-bin openmpi-common openmpi-doc libopenmpi-dev \
 && rm -rf /var/lib/apt/lists/*

# Minimal filesystem & shared area
RUN mkdir -p /var/run/sshd /shared /home/user/.ssh \
 && chmod 700 /home/user/.ssh

# Non-root user with passwordless sudo
RUN useradd -m -s /bin/bash user \
 && echo "user:userpassword" | chpasswd \
 && echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Harden SSH and enable pubkey auth
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config \
 && sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config \
 && sed -i 's|#AuthorizedKeysFile.*|AuthorizedKeysFile .ssh/authorized_keys|' /etc/ssh/sshd_config

# Authorized keys and private key for the 'user' account
COPY ssh_keys/id_rsa.pub /home/user/.ssh/authorized_keys
COPY ssh_keys/id_rsa     /home/user/.ssh/id_rsa

# Tighten key perms and set ownership
RUN chmod 600 /home/user/.ssh/id_rsa /home/user/.ssh/authorized_keys \
 && chown -R user:user /home/user/.ssh

# SSH port
EXPOSE 22

# Default context
USER user
WORKDIR /home/user

# Generate host keys, launch sshd in foreground, then adjust /shared perms
CMD sudo ssh-keygen -A && sudo /usr/sbin/sshd -D -e && sudo chown -R user:user /shared && sudo chmod -R 777 /shared
