# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
# Define environment variable
ENV TOKEN 1990575948:AAGIUQDT-MIf-p8oSNffBWkBsC_ys4bFKeE
ENV CHATID -1001531113599
ENV DELAY 60

# Run app.py when the container launches
CMD ["python", "main.py"]
