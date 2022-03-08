#################################################################
####################### BUILD STAGE #############################
################################################################
#################################################################
####################### BUILD STAGE #############################
#################################################################
# This image contains:
# 1. All the Python versions
# 2. required python headers
# 3. C compiler and developer tools
FROM snakepacker/python:all as builder

# Create virtualenv on python 3.9
# Target folder should be the same on the build stage and on the target stage
RUN python3.9 -m venv /usr/share/python3/app

# Install target package
ADD messenger /tmp/messenger

RUN /usr/share/python3/app/bin/pip install  pip==20.0.2

RUN /usr/share/python3/app/bin/pip install -U '/tmp/messenger'

# Will be find required system libraries and their packages
RUN find-libdeps /usr/share/python3/app > /usr/share/python3/app/pkgdeps.txt

#################################################################
####################### TARGET STAGE ############################
#################################################################
# Use the image version used on the build stage
FROM snakepacker/python:3.9

# Copy virtualenv to the target image
COPY --from=builder /usr/share/python3/app /usr/share/python3/app

# Install the required library packages
RUN cat /usr/share/python3/app/pkgdeps.txt | xargs apt-install

# Create a symlink to the target binary (just for convenience)
RUN ln -snf /usr/share/python3/app/bin/messenger-api /usr/bin/
RUN ln -snf /usr/share/python3/app/bin/analyzer-db /usr/bin/


#CMD ["sh", "-c", "analyzer-db revision --autogenerate; analyzer-db upgrade head; messenger-api"]
