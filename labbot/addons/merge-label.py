import logging
import os
import re

log = logging.getLogger("labbot.addon.merge_label")

title_regex = r"^(?:#|)(\d+)\s*"
word_regex = r"^#(\d+)$"

async def merge_request_hook(event, gl, *args, **kwargs):
    state = event.object_attributes["state"]
    related_issues = []

    conf = data.read_data()
    relation_keywords = conf["relation_keywords"]
    relation_distance = conf["relation_distance"]
    state_label = conf["state_label"]

    all_labels = list(state_label.values())

    try:
        label = state_label[state]
        if label in all_labels:
            all_labels.remove(label)

        remove_labels = ",".join(all_labels)

    except KeyError:
        # unknown state
        pass

    match = re.search(title_regex, event.object_attributes["title"])
    if match:
        related_issues.append(match.group(1))

    for line in event.object_attributes["description"].split("\\n"):
        line = line.lower()
        line_list = line.split(" ")

        for keyword in relation_keywords:
            try:
                keyword_index = line_list.index(keyword)

                min_pos = keyword_index - relation_distance
                if min_pos < 0:
                    min_pos = 0

                max_pos = keyword_index + relation_distance
                if max_pos >= len(line_list):
                    max_pos = len(line_list)-1

                for word in line_list[min_pos:max_pos+1]:
                    match = re.search(word_regex, word)
                    if match:
                        related_issues.append(match.group(1))

            except ValueError:
                pass

    related_string = ", ".join(related_issues)
    log.debug(f"Giving {label} to {related_string}")
    for issue in related_issues:
        if not issue: continue

        base_url = f"/projects/{event.project_id}/issues/{issue}"

        await gl.put(base_url, data={
            "add_labels": label,
            "remove_labels": remove_labels,
        })

def setup(bot):
    global data
    data = bot.get_data_container("merge-label", {
            "relation_keywords": [
                "related"
            ],
            "relation_distance": 2,

            "state_label": {
                "closed": "In Progress",
                "opened": "Code-Review",
                "merged": "C-R Bestanden",
            }
        })

    bot.register(merge_request_hook, "Merge Request Hook")
