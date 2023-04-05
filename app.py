import json
import requests
from flask import Flask
from flask import request
from flask import render_template

STATS = "11.23_stats.json"
ABLTS = "11.23_dmg_ablts.json"


app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    champion = request.args.get("champion", "")
    if champion:
        stats = display_stats(champion)
        abilities = display_abilities(champion)
    else:
        stats = ""
        abilities = ""
    return render_template('index.html', champion=champion, stats=stats, abilities=abilities)


def display_stats(champion):
    """Output designated champion's base statistics."""
    try:
        with open(STATS, 'r') as read_file:
            champion_stats = json.load(read_file)
            data = champion_stats[champion]

        health = data['health']
        health_g = data['health_g']
        armor = data['armor']
        armor_g = data['armor_g']
        magic_resist = data['magic_resist']
        magic_resist_g = data['magic_resist_g']
        attack_damage = data['attack_damage']
        attack_damage_g = data['attack_damage_g']
        stats = {'hp': health,
                 'hp_g': health_g,
                 'ar': armor,
                 'ar_g': armor_g,
                 'mr': magic_resist,
                 'mr_g': magic_resist_g,
                 'ad': attack_damage,
                 'ad_g': attack_damage_g}

        return stats

    except ValueError:

        return "invalid input"


def display_abilities(champion):
    """Output designated champion's abilities."""
    try:
        data = get_champ_data(champion)
        abilities = data['abilities']

        ablts = {}
        for key in abilities:
            parts = []
            for i in abilities[key]:
                name = i['name']
                effects = []
                for e in i['effects']:
                    desc = e['description']
                    attrs = []
                    if e['leveling']:
                        for a in e['leveling']:
                            attr = a['attribute']
                            mods = []
                            for m in a['modifiers']:
                                units = m['units'][0]
                                if units == "":
                                    mods.append({'base_vals': m['values']})
                                else:
                                    mods.append({'pct_val': m['values'][0],
                                                 'pct_units': units})

                            attribute = {'attribute': attr, 'modifiers': mods}
                            attrs.append(attribute)
                    effect = {'description': desc, 'leveling': attrs}
                    effects.append(effect)
                # cost = e['cost']['modifiers'][0]['values']
                # cooldown = e['cooldown']['modifiers'][0]['values']
                p = {'name': name, 'effects': effects}#, 'cost': cost, 'cooldown': cooldown}
                parts.append(p)
            ablts[key] = parts
        # print(json.dumps(abilities, indent=4))
        return abilities

    except ValueError:
        return "invalid input"


def get_champ_data(champion):
    """Makes request to get desired champion's JSON data for the latest available patch.

    The champion's name in the request URL is case-sensitive.
    """
    url = f"http://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions/{champion}.json"
    return requests.get(url).json()


if __name__ == "__main__":
    app.run(host=f"127.0.0.1", port=8080, debug=True)
