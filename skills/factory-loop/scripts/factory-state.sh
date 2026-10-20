#!/usr/bin/env bash
# Print the GitHub state of a repository's open Factory PRs as JSON.
# Usage: factory-state.sh <owner/repo> [pr-number ...]
# With PR numbers, reads only those PRs and skips the label filter (dry runs).
# Output: {"login", "fingerprint", "prs":[{..., "checks", "threads", "fingerprint"}]}
set -euo pipefail

repo="${1:?usage: factory-state.sh <owner/repo> [pr-number ...]}"
shift
owner="${repo%%/*}"
name="${repo#*/}"
marker='<!-- factory-review -->'
fields=number,state,title,url,author,isDraft,isCrossRepository,headRefName,headRefOid,baseRefName,mergeable,mergeStateStatus,reviewDecision,labels,createdAt

login="$(gh api user --jq .login)"

if [ "$#" -gt 0 ]; then
  prs="$(for n in "$@"; do gh pr view "$n" --repo "$repo" --json "$fields"; done | jq -s .)"
else
  prs="$(gh pr list --repo "$repo" --label factory --state open --limit 200 --json "$fields")"
fi

checks_for() {
  # `gh pr checks` exits 1 with "no checks reported" when a branch has none.
  local out
  if out="$(gh pr checks "$1" --repo "$repo" --json name,bucket,state,link 2>/dev/null)"; then
    printf '%s' "$out"
  else
    printf '[]'
  fi
}

threads_for() {
  gh api graphql --paginate --slurp -f owner="$owner" -f repo="$name" -F number="$1" -f query='
    query($owner:String!,$repo:String!,$number:Int!,$endCursor:String){
      repository(owner:$owner,name:$repo){ pullRequest(number:$number){
        reviewThreads(first:100,after:$endCursor){
          nodes{ id isResolved isOutdated path line
            first:comments(first:1){ totalCount nodes{ databaseId url body author{login} } }
            last:comments(last:1){ nodes{ body author{login} createdAt } } }
          pageInfo{ hasNextPage endCursor } } } } }' \
  | jq '[.[].data.repository.pullRequest.reviewThreads.nodes[]]'
}

result='[]'
for n in $(jq -r 'sort_by(.createdAt) | .[].number' <<<"$prs"); do
  pr="$(jq --argjson n "$n" '.[] | select(.number == $n)' <<<"$prs")"
  checks="$(checks_for "$n")"
  threads="$(threads_for "$n")"
  entry="$(jq -n --argjson pr "$pr" --argjson checks "$checks" --argjson threads "$threads" \
    --arg login "$login" --arg marker "$marker" '
    def bucket($b): [$checks[] | select(.bucket == $b)] | length;
    ($threads | map(select(.isResolved | not)) | map({
      id, isOutdated, path, line,
      item: ("c" + (.first.nodes[0].databaseId | tostring)),
      url: .first.nodes[0].url,
      kind: (if .first.nodes[0].author.login == $login and (.first.nodes[0].body | contains($marker))
             then "factory" else "human" end),
      comments: .first.totalCount,
      lastAt: .last.nodes[0].createdAt,
      waitingOnHuman: (.last.nodes[0].author.login == $login and
        (.last.nodes[0].body | test("^Factory resolution: (disputed|unable-to-verify)")))
    })) as $open
    | ($pr | del(.labels, .author) + {
        author: .author.login,
        factoryLabel: ([.labels[].name] | index("factory") != null),
        checks: {
          total: ($checks | length),
          pass: bucket("pass"), skipping: bucket("skipping"), pending: bucket("pending"),
          fail: bucket("fail"), cancel: bucket("cancel"),
          failing: [$checks[] | select(.bucket == "fail" or .bucket == "cancel") | {name, bucket, link}]
        },
        threads: $open
      })
    | . + {fingerprint: ([.headRefOid, .isDraft, .mergeable, .mergeStateStatus, .reviewDecision,
        .factoryLabel, ($checks | map(.name + "=" + .bucket) | sort),
        ($open | map(.item + ":" + (.comments | tostring)) | sort)] | tojson)}')"
  fp="$(jq -r .fingerprint <<<"$entry" | sha256sum | cut -c1-16)"
  result="$(jq --argjson e "$entry" --arg fp "$fp" '. + [$e + {fingerprint: $fp}]' <<<"$result")"
done

jq -n --arg login "$login" --argjson prs "$result" \
  '{login: $login, fingerprint: ($prs | map((.number | tostring) + ":" + .fingerprint) | join(",")), prs: $prs}'
