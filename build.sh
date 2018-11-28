pip freeze > requirements.txt
docker build -t tikz/ns2sud-web .
docker push tikz/ns2sud-web