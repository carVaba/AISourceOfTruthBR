# AI Brain: Unified Configuration and Rules

These global rules apply to all AI assistants (AGY CLI, Claude Code CLI, Copilot CLI) across every project and session.

---

## 1. Global Assistant Rules

### Communication Language
Always use ASD-STE100 Simplified Technical English when you talk to the user.

Apply these writing rules:
- Write short sentences. Use a maximum of 20 words for an instruction. Use a maximum of 25 words for a description.
- Write one instruction in one sentence.
- Use the active voice. Do not use the passive voice.
- Use simple verb tenses. Prefer the present tense.
- Use one word for one meaning. Do not use synonyms for the same idea.
- Do not use noun clusters of more than three words.
- Use a maximum of six sentences in a paragraph.
- Use lists and tables for steps and for data.
- Do not use idioms, jargon, or figures of speech.

This rule applies to conversational replies and commit messages. It does not control the programming language or file naming rules.

### Editor Selection
- Always use `nvim` instead of `vim`.

### Git Commit Authorship
- Do not add a "Co-Authored-By" line for Claude, Gemini, Copilot, or any AI assistant in a commit message. Company policy prohibits AI co-authorship attribution.

---

## 2. iOS Project Standards

### Stop Over-Engineering (Keep It Simple)
- Do not make premature abstractions. Write only the code necessary for the current task.
- Do not make generic protocols or base classes unless you receive an explicit instruction.
- Keep SwiftUI views simple and focused purely on presentation logic.
- **Dedicated Views over Computed Properties**: Always create views as separate `struct` types instead of computed properties (`var myView: some View`) or helper functions.
  - A separate `struct View` creates an explicit invalidation boundary for SwiftUI.
  - During updates, SwiftUI evaluates each view struct boundary to decide whether it needs to run its `body`.
  - Computed properties do not create an invalidation boundary and force the whole parent view to recalculate.
- Avoid mega `var body` declarations. Break views into smaller component structs if they exceed 80 lines.
- **State Locality**: Place `@State` properties locally in the child view that owns them to prevent full tree reconstructions.
- **Data Scoping**: Pass only the exact data a child view requires to render. Do not pass entire parent models down if only individual fields are needed.

### Stop Over-Documentation
- Do not write comments that explain *what* the code does. The code must be self-explanatory.
- Write comments only to explain *why* you chose a specific complex solution.
- Do not add DocC comments unless explicitly requested.
- Maximum 3 lines of comments, with a maximum of 120 characters per line.
- Use Documentation search for Apple API questions.
- Do not hallucinate API names. Verify with the documentation first.
- Prefer `async`/`await` over completion handlers.
- Use structured concurrency (`TaskGroup`, `async let`) over manual task management.
- Error handling: use typed throws where supported.

### iOS and Swift Implementation Rules
- **State Management**: Always prefer the `@Observable` macro over `ObservableObject` and `@Published` (if supported by the project target; otherwise maintain the existing pattern).
  - `@Observable` tracks access at the property level, refreshing only the views that read the modified property.
  - Pass `@Observable` models into subviews directly or via `.environment()` and read them using `@Environment`.
  - Use `@Bindable` when you need two-way bindings to an `@Observable` model inside a view.
- **Closures in Views**: Avoid storing escaping closures or `@ViewBuilder` closures in view structs. Evaluate closures during view initialization to prevent unnecessary invalidation loops.
- **Safety**: Do not use force unwraps (`!`) or force casts (`as!`).
- **Memory Management**: Prevent retain cycles. Always use `[weak self]` in closures that capture `self`.
- **Project File**: Keep the `.pbxproj` file clean. Do not manually edit the Xcode project file at first; use `kintsugi`. If the tool cannot solve the issue, edit manually.
- **Actor Isolation**: Default to `@MainActor` for UI components, ViewModels, and UI state models. Only leave the main actor when you intentionally execute heavy background computation or I/O.
- **Actor Reentrancy**: Handle reentrancy at `await` suspension points on custom actors by caching in-flight `Task` instances to prevent duplicate concurrent network or disk operations.
- **Protocol Naming**: Follow Apple guidelines by naming ability protocols as adjectives ending in "-able", "-ible", or "-ing".

### Testing Standards
- Organize test methods into clear Arrange, Act, and Assert (AAA) phases with blank lines between them.
- Follow Test-Driven Development (TDD) cycles: Red, Green, Refactor.
- Test business logic and state changes with fast unit tests instead of slow UI tests.
- Declare stored properties in `XCTestCase` as implicitly unwrapped optionals (`!`), initialize in `setUp()`, and set them to `nil` in `tearDown()` (this does not apply to Falabella submodules and the main app, Tottus, and Sodimac, which use a dedicated test library).

### CI/CD and Workflows
- Refer to `Fastfile` to verify deployment steps.
- Use `bundle exec fastlane` to run lanes.
- Refer to `.gitlab-ci.yml` to understand the CI pipeline.
- Refer to GitHub workflow or action configuration files to inspect CI workflows.

---

## 3. Falabella Project: AI Memory Management

- Write important data to an AI memory file (for example: `ios-browse.md`) every time you complete a task.
- Save all AI memory files in this exact directory: `/Users/alfbaro-mac-pro/Developer/Falabella/`.
- Create the memory file if it does not exist.
- Write technical data that helps in future tasks, including:
  - Architecture rules and discoveries.
  - Firebase Remote Config changes.
  - Recommendations to refactor code.
- Read these `.md` files at the start of a new session. These files contain primary project context.
- Format these files to maximize model parsing and understanding across future sessions.
