"""
automatically labels issues referenced in merge requests with
specified labels.
"""

import os
import re
import logging

log = logging.getLogger(__name__)


title_regex = r"^(?:#|)(\d+)\s*"
word_regex = r"^#(\d+)$"
relation_keywords = [
    "related"
]
relation_distance = 2

state_label = {
    "closed": "In Progress",
    "opened": "Code-Review",
    "merged": "C-R Bestanden",
}

# Extra labels that the bot will check for before acting
act_labels = [
    "Sprint",
    "Testing",
    "TestingFailed",
]

async def merge_label_hook(event, gl, *args, **kwargs):
    state = event.object_attributes["state"]
    related_issues = []

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

    for issue in related_issues:
        if not issue: continue

        base_url = f"/projects/{event.project_id}/issues/{issue}"

        has_label = False
        issue_data = await gl.getitem(base_url)
        for label in issue_data["labels"]:
            if label in act_labels or state_label.values():
                has_label = True
                break

        if not has_label:
            log.debug(f"Issue #{issue} does not have a relevant label")
            continue

        delete_labels = act_labels + list(state_label.values())

        try:
            label = state_label[state]
            if label in delete_labels:
                delete_labels.remove(label)

            remove_labels = ",".join(delete_labels)

            await gl.put(base_url, data={
                "add_labels": label,
                "remove_labels": remove_labels,
            })

        except KeyError:
            log.exception("Unknown state")

def setup(bot) -> None:
    bot.register_merge_hook(merge_label_hook)
