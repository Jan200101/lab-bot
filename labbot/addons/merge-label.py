"""
automatically labels issues referenced in merge requests with
specified labels.
"""

import os
import re
import logging

from labbot.config import Config

log = logging.getLogger(__name__)

config = Config(__name__)
config.set_global_data(
    title_regex = r"^(?:#|)(\d+)\s*",
    word_regex = r"^#(\d+)$",

    relation_keywords = [
        "related"
    ],
    relation_distance = 2,

    state_label = {
        "closed": "In Progress",
        "opened": "Code-Review",
        "merged": "C-R Bestanden",
    },

    act_labels = [
        "Sprint",
        "Testing",
        "TestingFailed",
    ]
)

@config.config_decorator()
async def merge_label_hook(event, gl, *args, **kwargs):
    title = event.object_attributes["title"]
    description = event.object_attributes["description"]
    state = event.object_attributes["state"]
    related_issues = []

    if not description or title.lower().startswith("draft"):
        return

    match = re.search(config["title_regex"], title)
    if match:
        related_issues.append(match.group(1))

    for line in description.split("\\n"):
        line = line.lower()
        line_list = line.split(" ")

        for keyword in config["relation_keywords"]:
            try:
                keyword_index = line_list.index(keyword)

                min_pos = keyword_index - config["relation_distance"]
                if min_pos < 0:
                    min_pos = 0

                max_pos = keyword_index + config["relation_distance"]
                if max_pos >= len(line_list):
                    max_pos = len(line_list)-1

                for word in line_list[min_pos:max_pos+1]:
                    match = re.search(config["word_regex"], word)
                    if match:
                        related_issues.append(match.group(1))

            except ValueError:
                pass

    for issue in related_issues:
        if not issue: continue

        base_url = f"/projects/{event.project_id}/issues/{issue}"

        has_label = False
        issue_data = await gl.getitem(base_url)
        issue_labels = issue_data["labels"]
        for label in issue_labels:
            if label in config["act_labels"] or label in config["state_label"].values():
                has_label = True
                break

        if not has_label:
            label_str = ", ".join(issue_labels)
            log.debug(f"Issue #{issue}({event.project_id}) does not have a relevant label (has: '{label_str}')")
            continue

        delete_labels = config["act_labels"] + list(config["state_label"].values())

        try:
            label = config["state_label"][state]
            if label in delete_labels:
                delete_labels.remove(label)

            remove_labels = ",".join(delete_labels)
            log.debug(f"Applying {label} to {issue}")
            if remove_labels:
                log.debug(f"Removing `{remove_labels} from {issue}")
            await gl.put(base_url, data={
                "add_labels": label,
                "remove_labels": remove_labels,
            })

        except KeyError:
            log.exception("Unknown state")

def setup(bot) -> None:
    config.setup(__name__, bot.name)
    bot.register_merge_hook(merge_label_hook)
