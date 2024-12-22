#!/bin/bash
if [ -z "$HOST_USER" ]; then
    HOST_USER=user
fi
if ! id "$HOST_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$HOST_USER"
    echo "$HOST_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
fi
export PS1="${HOST_USER}@brainframe-cli:\w\$ "
echo "export PS1=\"${PS1}\"" >> /home/$HOST_USER/.bashrc

echo "display_shell_en() { cat /shell.en; }" >> /home/$HOST_USER/.bashrc
echo "display_shell_en" >> /home/$HOST_USER/.bashrc

exec su - $HOST_USER -c "cd /host && script -qec bash /dev/null"
