билд
docker build -t split .

запуск
sudo docker run -d -it --rm -v "/home/dr/split:/working" --restart on-failure --name split split:latest



запуск локально для тестов
docker run -d -v "c:/tmp/working:/working" -it --rm split:latest




