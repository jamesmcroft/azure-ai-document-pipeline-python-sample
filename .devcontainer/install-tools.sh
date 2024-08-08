curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor >microsoft.gpg
mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

sh -c 'echo "deb [arch=$(dpkg --print-architecture)] https://packages.microsoft.com/debian/$(lsb_release -rs | cut -d'.' -f 1)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'

apt-get update &&
    apt-get upgrade -y &&
    export DEBIAN_FRONTEND=noninteractive &&
    apt-get -y install --no-install-recommends \
        poppler-utils \
        azure-functions-core-tools-4
