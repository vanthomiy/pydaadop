# How to Work with OpenCode Agents (Docker-Only)

## Workflow Phases

1. **Planning**
   - Agent thinks about the task and creates a meaningful plan.
   - Breaks the task into objectives, questions, and todos.

2. **Clarification**
   - If anything is ambiguous, agent asks the user concise clarifying questions.

3. **Todo Creation**
   - Convert plan into concrete, actionable steps.

4. **Implementation**
   - Agent executes each step in containers only.
   - Ensures actions are self-contained and reproducible.

5. **Testing / Verification**
   - Agent validates results against the plan.
   - Detects errors, missing requirements, or unexpected outputs.

6. **Iteration**
   - If requirements are not met, agent loops:
     - Updates todos if needed.
     - Re-implements and retests.
   - Repeats until results match the plan.

7. **Finalization**
   - Agent updates the plan with a short summary of completed work.
   - Communicates to the user only:
     - What was done
     - Problems? (if any)
     - Questions? (if any)
     - Next steps? (if any)