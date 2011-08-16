from pprint import pformat
import os

venv = os.environ.get("VIRTUAL_ENV")

execfile(venv+"/src/osha.theme/src/osha/theme/skins/osha_theme_custom_templates"
         "/napofilmstructure.py")
old_films = Films

execfile(venv+"/src/osha.policy/src/osha/policy/data/multimedia/napofilm.py")
new_films = filmstructure


for i in range(len(old_films)):
    old_film = old_films[i][1]
    new_film = new_films[i]
    new_film["video_avi"] = old_film["durlavi"]
    new_film["video_wmv"] = old_film["durlwmv"]
    for j in range(len(old_film["episodes"])):
        old_episode = old_film["episodes"][j]
        new_episode = new_film["episodes"][j]
        new_episode["video_avi"] = old_episode["durlavi"]
        new_episode["video_wmv"] = old_episode["durlwmv"]

new_films_structure = pformat(new_films)
merged_films = open("merged_films_structure.py", "w")
merged_films.write(new_films_structure)
