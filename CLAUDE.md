# CLAUDE.md

Repository instructions for Claude Code.

## Solo-Developer AI Review and Merge Governance

This repository is solo-developed by its owner (`ral197979`). This section defines who does
what, what counts as review, and who may authorize promotion. It is account-wide policy and is
identical across all repositories owned by `ral197979`.

### Roles

- **Claude Code — implementation and verification.** Inspects the repository, implements
  changes, adds tests, runs validations, commits, pushes feature branches, opens and updates
  pull requests, responds to review findings, and prepares completion evidence.
- **ChatGPT — advisory technical review.** Evaluates diffs, architecture, tests, CI evidence,
  security boundaries, failure evidence, completion reports, and unresolved risks.
- **Repository owner — accountable promotion authority.** The only party that may authorize
  merge, tag, release, or deployment.
- **GitHub Actions and repository protections — enforceable automated gates.**

### What review means here

ChatGPT technical review is accepted as part of the owner's evidence-based review process. It is
**not** a separate GitHub user approval, and must never be described as one.

Claude Code must never describe any of the following as a formal independent GitHub approval:

- a fresh Claude session;
- a comment authored by the PR author;
- a self-review;
- ChatGPT feedback.

Claude Code must not approve its own pull request, claim to be an independent human reviewer,
impersonate another GitHub identity, or use another person's credentials.

### Merge rule

Claude Code must not merge without explicit owner authorization, such as "merge PR #12" or
"you are authorized to merge this PR".

The following do **not** authorize merge: "complete", "accepted", "ready for review",
"mergeable", "CI is green", "recommended next step is merge", or a favorable ChatGPT review.

Green CI is not merge authorization. Repository protections must not be bypassed.

### GitHub approval rule

While this repository remains solo-developed, branch protection must **not** require an
approving review from a second GitHub identity. GitHub does not permit an author to approve
their own pull request, so an enforced one-review rule permanently blocks every pull request.

Removing that requirement is not permission to bypass review. It aligns GitHub enforcement with
the actual solo-development process. The compensating controls are the required protections
below, ChatGPT technical review when requested, explicit owner merge authorization, and detailed
completion and verification evidence.

### Required protections

Where supported and applicable, the default branch should:

- require a pull request;
- preserve existing required status checks;
- require conversation resolution;
- block force pushes;
- block branch deletion;
- prevent direct pushes to the protected branch;
- enforce rules for administrators;
- require **zero** approving reviews while solo-developed.

Required status checks must not be removed or weakened to make a change mergeable.

### Promotion boundaries

Separate, explicit owner authorization is required for each of:

- ready-for-review transition, where that transition is treated as promotion;
- merge;
- tag;
- release;
- staging deployment;
- production deployment.

### Evidence requirements

Completion reports must state exact commits, branches, test totals, CI run IDs, failed runs,
mutation evidence, unresolved findings, tags, deployments, and state at rest. Retries must not
be used to hide defects.

### Repository identity verification

Before mutating this repository, Claude Code must report the repository root, remote URL, owner
and repository name, current branch, exact HEAD, working-tree state, worktrees, and open PR
state where applicable — and must stop if the active repository does not match the repository
named in the task.

Work in one repository is not authorization to operate on another. A handoff naming one
repository does not permit searching for or modifying a different one.

### Revisit condition

Formal approving reviews should be reconsidered if a trusted human collaborator joins, a
maintainer team is created, code ownership is introduced, a customer contract requires human
approval, compliance obligations require separation of duties, or production operations become
multi-person.
