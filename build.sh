cd app
../venv/Scripts/pybabel extract -F babel.cfg -o messages.pot .
../venv/Scripts/pybabel init -i messages-es.pot -d translations -l es
../venv/Scripts/pybabel init -i messages-pt.pot -d translations -l pt
../venv/Scripts/pybabel compile -d translations
cd ..
./venv/Scripts/pip freeze > requirements.txt
docker build -t tikz/ns2sud-web .
docker push tikz/ns2sud-web