FROM ubuntu:22.04

# Set default environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="America/New_York"

# Create working directory and relevant dirs
WORKDIR /app

# Install deps from APT
RUN apt-get update && apt-get install -y \
  tzdata \
  wget \
  gpg \
  python3 \ 
  python3-pip \
  xvfb \
  xfonts-cyrillic \
  xfonts-100dpi \
  xfonts-75dpi \
  xfonts-base \
  xfonts-scalable \
  gtk2-engines-pixbuf \
&& rm -rf /var/lib/apt/lists/*

# Download and install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \ 
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get -y install google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Install bot Python deps
ADD ./requirements.txt .
RUN pip install -r ./requirements.txt            

# Add often-changed files in order to cache above
ADD ./main.py .
ADD ./entrypoint.sh .

# Make the entrypoint executable
RUN chmod +x entrypoint.sh

# Set the entrypoint to our entrypoint.sh                                                                                                                     
ENTRYPOINT ["/app/entrypoint.sh"] 