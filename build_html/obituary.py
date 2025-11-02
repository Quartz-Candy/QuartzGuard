from operator import itemgetter
from build_html import html_table
import time
import json


def obituary_html(player, death_msg, time_of_death, uuid, stats):
    html = [_player_info(player, death_msg, time_of_death, uuid)]

    for entry in _create_stats(stats).items():
        html.append(f'<h2>-- {entry[0].capitalize()} Stats --</h2>')
        html.append(html_table.create_table(entry[1]))

    return "".join(html)


def _player_info(player, death_msg, time_of_death, uuid):
    datetime =  f"{time.strftime(f"%B %d %Y {time_of_death} UTC: %z", time.localtime())}"
    death_msg = death_msg.replace(f"{player} ", "").capitalize()

    return (
        '<center>'
        f'<p class="has-text-align-center has-medium-font-size"><strong>Time of Death:</strong> {datetime}</p>'
        f'<p class="has-text-align-center has-medium-font-size"><strong>Cause of Death:</strong> {death_msg}</p>'
        '<div class="wp-block-image">'
        f'<figure class="aligncenter size-large"><img decoding="async" src="https://mc-heads.net/body/{uuid}/left" alt=""></figure></div>'
        '<hr>'
    )

    return (
        '<div class="wp-block-columns is-layout-flex">'
        '<div class="wp-block-column is-vertically-aligned-center">'
        f'<p class="has-text-align-right has-medium-font-size"><strong>Time of Death:</strong> {datetime}</p>'
        f'<p class="has-text-align-right has-medium-font-size"><strong>Cause of Death:</strong> {death_msg}</p>'
        '</div>'
        '<div class="wp-block-column is-vertically-aligned-center">'
        f'<figure class="wp-block-image size-large"><img decoding="async" src="https://mc-heads.net/body/{uuid}/left" alt=""></figure>'
        '</div>'
        '</div>'
        '<hr>'
    )


def _get_mc_time(seconds):
    result = []

    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result)


def _create_stats(stats_file):
    stat_content = json.loads(stats_file)["stats"]

    general_stats = []
    mined_stats = []
    items_broken_stats = []
    items_crafted_stats = []
    items_used_stats = []
    items_picked_up = []
    items_dropped_stats = []
    entities_killed_stats = []

    for stat_type, values in stat_content.items():
        if stat_type == "minecraft:custom":
            for key, value in values.items():
                clean_key = key.replace("minecraft:", "").replace("_", " ").title()
                if "time" in key:
                    general_stats.append([clean_key, _get_mc_time(value / 20)])
                elif "aviate" in key:
                    general_stats.append(["Elytra", f"{value/100:.0f} blocks"])
                elif "cm" in key:
                    general_stats.append([clean_key.replace(" One Cm", ""), f"{value/100:.0f} blocks"])
                elif "damage" in key:
                    general_stats.append([clean_key, f"{value * 0.1:.1f} hearts"])
                else:
                    general_stats.append([clean_key, value])

        elif stat_type == "minecraft:mined":
            mined_stats += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

        elif stat_type == "minecraft:broken":
            items_broken_stats += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

        elif stat_type == "minecraft:crafted":
            items_crafted_stats += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

        elif stat_type == "minecraft:used":
            items_used_stats += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

        elif stat_type == "minecraft:picked_up":
            items_picked_up += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

        elif stat_type == "minecraft:dropped":
            items_dropped_stats += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

        elif stat_type == "minecraft:killed":
            entities_killed_stats += [[k.replace("minecraft:", "").replace("_", " ").title(), v] for k, v in values.items()]

    return {
        "general": sorted(general_stats, key=itemgetter(0)),
        "mined": sorted(mined_stats, key=itemgetter(0)),
        "broken": sorted(items_broken_stats, key=itemgetter(0)),
        "crafted": sorted(items_crafted_stats, key=itemgetter(0)),
        "used": sorted(items_used_stats, key=itemgetter(0)),
        "picked_up": sorted(items_picked_up, key=itemgetter(0)),
        "dropped": sorted(items_dropped_stats, key=itemgetter(0)),
        "killed": sorted(entities_killed_stats, key=itemgetter(0))
    }