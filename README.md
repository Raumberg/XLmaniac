# Excel Maniac
## An application build with pure pandas to automate Excel Registers for company
Note: Rather unfinished version
### The purpose is to prepare a dataset of the clients to serialize/deserialize further loads to a database
Technologies:
* Pure pandas implementation
* Scalable architecture (at least I'm tryin')
* Flet framework (Flutter app builder)
### Future plans and todos:
* Rebuild with web and docker-compose containerization

Also note for those who will find this repo: 
This will be probably very useless since I cannot imagine any implementations outside the company. This repo is pushed for demonstrational purposes.

If you want to somehow run it:
```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
python /main.py # or flet run (--web for web version) /main.py
```