# Sync Protocols

## Overview
This document outlines the standard procedures for synchronizing the local Scova codebase with the remote repository.

## Pre-Sync Checklist
1.  **Tests**: Ensure all relevant tests (including Chaos Monkey) pass locally.
2.  **Updates Log**: Ensure `management/updates.md` has been updated with a new entry describing your changes.

## Sync Workflow
Run the following commands in the terminal:

1.  **Fetch & Rebase** (to get latest remote changes):
    ```bash
    git pull --rebase origin main
    ```

2.  **Add Changes**:
    ```bash
    git add .
    ```

3.  **Commit**:
    -   **Content Consistency**: The commit message and the entry in `updates.md` must contain the **same information**.
    -   **Tone & Style**: Use the descriptive, narrative style found in `updates.md`. Avoid cryptic one-liners.
    -   **Format**:
        -   *Commit Message*: Concise summary line, followed by a bulleted list of details.
        -   *Updates Log*: Date/Time header, followed by the same bulleted list.
    ```bash
    git commit -m "feat: Implemented Dynamic 2D Plane

    - Implemented DynamicPlaneProcessor for vector space transformation.
    - Integrated processor into TrainingWorker.
    - Added decoder for inverse transformation."
    ```

4.  **Push**:
    ```bash
    git push origin main
    ```

## Handling Conflicts
-   If `git pull --rebase` triggers a conflict, resolve it using the IDE's merge tool.
-   After resolving, continue the rebase: `git rebase --continue`.
-   **Never** force push (`git push -f`) unless explicitly authorized for emergency recovery.
