"""
once an issue is assigned a specific label
create merge requests for each branch related to that issue
branch relation is figured out by looking at related merge requests
"""

import logging

from labbot.config import Config

log = logging.getLogger(__name__)

config = Config()
config.set_global_data(
    stable_branch = "main",
    staging_branch = "staging",
    merge_label = "Release",
)

@config.config_decorator()
async def issue_update_hook(event, gl, *args, **kwargs):
    issue_id = event.object_attributes["iid"]
    issue_url = f"/projects/{event.project_id}/issues/{issue_id}"
    issue_data = await gl.getitem(issue_url)


    branches = {}
    if config["merge_label"] in issue_data["labels"]:
        async for merge_data in gl.getiter(f"{issue_url}/related_merge_requests"):
            source_branch = merge_data["source_branch"]
            target_branch = merge_data["target_branch"]
            merge_id = merge_data["iid"]

            # we only want staging merges
            if target_branch != config["staging_branch"]:
                continue

            if not source_branch in branches:
                branches[source_branch] = []
            branches[source_branch].append(f"!{merge_id}")

    if branches:
        branch_str = ", ".join(branches.keys())
        log.debug(f"`{branch_str}`({event.project_id}) are ready to be merged into stable")

    merge_url = f"/projects/{event.project_id}/merge_requests"
    for branch, merge in branches.items():
        merges_exists = 0

        async for merge_data in gl.getiter(merge_url, params={
            "source_branch": branch,
            "target_branch": config["stable_branch"]
        }):
            # We found a merge request, add it to the counter
            merges_exists += 1
            if merges_exists > 3:
                break

        if merges_exists > 3:
            log.debug(f"merges for `{branch}` already exists, not opening more than 3")
        else:
            if merges_exists:
                log.debug(f"merge for `{branch}` already exists, opening a new one regardless")

            merge_string = ", ".join(merge)
            await gl.post(merge_url, data={
                "source_branch": branch,
                "target_branch": config["stable_branch"],
                "title": f"[stable] Merge `{branch}` into `{config['stable_branch']}`",
                "description": f"Related to #{issue_id}    \n    \nStaging Merges:    \n{merge_string}"
            })


def setup(bot) -> None:
    config.setup(__name__, bot.name)
    bot.register_issue_hook(issue_update_hook)
