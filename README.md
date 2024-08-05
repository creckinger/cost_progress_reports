# cost_progress_reports
Cost Progress Reports Generator




## Transform and Transfer into Docker Image
### Prerequisites
sudo apk update
sudo apk add docker
sudo rc-update add docker boot
sudo service docker start

## Transform into Docker Image
- Go into the base directory of the app
- Run: docker build -t cprapp .      
- Try your image with: docker run -p 5001:5000 cprapp       
- Save it as a file: docker save -o cprapp.tar cprapp
- Transfer the file via ssh to the linux server: scp cprapp.tar user@your_alpine_server_ip:/path/to/directory
- Load the file inside the linux server: docker load -i /path/to/directory/cprapp.tar
- Run the app inside the docker container in linux: docker run -d -p 5000:5000 --name cprapp cprapp

### Update a running Docker App
List Running Containers:
Find the running container with the name cprapp.
docker ps

Stop the Existing Container:
Stop the container using its container ID or name.
docker stop cprapp

Remove the Existing Container:
Remove the stopped container.
docker rm cprapp

Run the New Container:
Now you can run the new version of your Docker image.
docker run -d -p 5000:5000 --name cprapp cprapp:latest



