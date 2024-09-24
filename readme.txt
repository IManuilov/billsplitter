билд
docker build -t split .

запуск
sudo docker run -d -it --rm -v "/home/dr/split:/working" --restart on-failure --name split split:latest


docker run -d -v "c:/tmp/working:/working" -it --rm split:latest




