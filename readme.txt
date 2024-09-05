docker build -t split .


docker run -d -v "/home/ec2-user/working:/working" -it --rm split:latest

docker run -d -v "c:/tmp/working:/working" -it --rm split:latest


sudo docker run -v "/home/dr/split:/working" -it --rm split:latest
