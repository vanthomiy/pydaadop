# git-workflow Plan

## Objective
Implement Git commit/push/branch workflow using OpenCode agent **entirely in Docker**.

## Todos
- [ ] Create branch container
- [ ] Stage and commit in container
- [ ] Push from container
- [ ] Create PR container

## Notes / Questions
- Default base branch for PR?
- Should PR auto-merge or wait for review?

## Implementation Summary
- All steps run in containers.
- Branch created, commit staged and pushed.
- PR creation prepared via GitHub CLI container.