"""
once an issue is assigned a specific label
create merge requests for each branch related to that issue
branch relation is figured out by looking at related merge requests
"""

import logging

log = logging.getLogger(__name__)


stable_branch = "main"
staging_branch = "staging"
merge_label = "Release"

async def issue_update_hook(event, gl, *args, **kwargs):
    issue_id = event.object_attributes["iid"]
    issue_url = f"/projects/{event.project_id}/issues/{issue_id}"
    issue_data = await gl.getitem(issue_url)


    branches = {}
    if merge_label in issue_data["labels"]:
        async for merge_data in gl.getiter(f"{issue_url}/related_merge_requests"):
            source_branch = merge_data["source_branch"]
            target_branch = merge_data["target_branch"]
            merge_id = merge_data["iid"]

            # we only want staging merges
            if target_branch != staging_branch:
                continue

            if not source_branch in branches:
                branches[source_branch] = []
            branches[source_branch].append(f"!{merge_id}")

    if branches:
        branch_str = ", ".join(branches.keys())
        log.debug(f"`{branch_str}` are ready to be merged into stable")

    merge_url = f"/projects/{event.project_id}/merge_requests"
    for branch, merge in branches.items():
        merge_exists = False

        async for merge_data in gl.getiter(merge_url, params={
            "source_branch": branch,
            "target_branch": stable_branch
        }):
            if merge_data["state"] == "opened":
                merge_exists = True

        if merge_exists:
            log.debug(f"merge for `{branch}` already exists")
        else:
            merge_string = ", ".join(merge)
            await gl.post(merge_url, data={
                "source_branch": branch,
                "target_branch": stable_branch,
                "title": f"[stable] Merge `{branch}` into `{stable_branch}`",
                "description": f"Related to #{issue_id}    \n    \nStaging Merges:    \n{merge_string}"
            })


def setup(bot) -> None:
    bot.register_issue_hook(issue_update_hook)