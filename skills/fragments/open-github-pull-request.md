# Open a GitHub Pull Request

1. Stage only the files that belong to the task.
2. Commit all task changes before you open the pull request.
3. Confirm that you pushed every commit.
4. Confirm that the local task branch is synchronized with its upstream branch.
5. Open a draft pull request by default:

   ```bash
   gh pr create --draft --base <parent>
   ```

6. Use the established parent branch for `<parent>`.
7. Only when the user requests a ready-for-review pull request, create that type of pull request.
8. If `gh` is not available or authenticated, keep the branch pushed.
9. If `gh` is not available or authenticated, report the repository compare URL and the exact blocker.
10. If `gh` is not available or authenticated, do not retry with other tools.
11. Include this information in the pull request body:

    - A summary of the user-facing or developer-facing change
    - Important implementation information for the review
    - The validation commands and their results
    - Known gaps, skipped checks, and follow-up work
    - Screenshots or artifact links when the change affects the UI or visual behavior.

12. If the user does not request a merge, do not merge the pull request.
13. If the user does not request a ready state, do not mark the pull request as ready.
14. If the user does not request reviewers, do not request reviewers.
15. If the user does not request a settings change, do not change remote repository settings.
16. Report the following results:

    - The pull request URL
    - The branch name
    - The pushed commits
    - The validation results
    - The unresolved risks.

17. If you cannot open the pull request, report the exact blocker.
18. If you cannot open the pull request, keep the pushed branch available for review.
