# Global rules

These rules apply to every project and every session.

## Language of replies
These rules also apply to all project commit messages.

Always use ASD-STE100 Simplified Technical English when you talk to the user.

Apply these writing rules:

- Write short sentences. Use a maximum of 20 words for an instruction. Use a maximum of 25 words
  for a description.
- Write one instruction in one sentence.
- Use the active voice. Do not use the passive voice.
- Use simple verb tenses. Prefer the present tense.
- Use one word for one meaning. Do not use synonyms for the same idea.
- Do not use noun clusters of more than three words.
- Use a maximum of six sentences in a paragraph.
- Use lists and tables for steps and for data.
- Do not use idioms, jargon, or figures of speech.

This rule is for the replies in the conversation. It does not set the language of the files that
you write. Each project can have a different rule for its files.

## Git commit authorship

Do not add a "Co-Authored-By" line for Claude or any AI in a commit message. Company policy
does not allow an AI co-author on a commit.

# iOS Project Rules

## 1. Stop Over-Engineering (Keep It Simple)
* Do not make premature abstractions. Write only the code necessary for the current task.
* Do not make generic protocols or base classes unless you receive an explicit instruction.
* Keep SwiftUI views simple and focused purely on presentation logic.
* **Dedicated Views over Computed Properties**: Always create views as separate `struct` types instead of computed properties (`var myView: some View`) or helper functions.
  * A separate `struct View` creates an explicit invalidation boundary for SwiftUI.
  * During updates, SwiftUI evaluates each view struct boundary to decide whether it needs to run its `body`.
  * Computed properties do not create an invalidation boundary and force the whole parent view to recalculate.
* Avoid mega `var body` declarations. Break views into smaller component structs if they exceed 80 lines.
* **State Locality**: Place `@State` properties locally in the child view that owns them to prevent full tree reconstructions.
* **Data Scoping**: Pass only the exact data a child view requires to render. Do not pass entire parent models down if only individual fields are needed.

## 2. Stop Over-Documentation
* Do not write comments that explain *what* the code does. The code must be self-explanatory.
* Write comments only to explain *why* you chose a specific complex solution.
* Do not add DocC comments unless I explicitly tell you.
* Max 3 lines, with 120 characters per line.
* Use Documentation search for Apple API questions.
* Do NOT hallucinate API names - Verify with the docs first.
* Prefer async/await - never completion handlers.
* Use structured concurrency (`TaskGroup`, `async let`) over manual task management.
* Error handling: use typed throws where supported.

## 3. iOS and Swift Rules
* **State Management**: Always prefer the `@Observable` macro over `ObservableObject` and `@Published`(if the project supported otherwise keep the old way).
  * `@Observable` tracks access at the property level, refreshing only the views that read the modified property.
  * Pass `@Observable` models into subviews directly or via `.environment()` and read them using `@Environment`.
  * Use `@Bindable` when you need two-way bindings to an `@Observable` model inside a view.
* **Closures in Views**: Avoid storing escaping closures or `@ViewBuilder` closures in view structs. Evaluate closures during view initialization to prevent unnecessary invalidation loops.
* **Safety**: Do not use force unwraps (`!`) or force casts (`as!`).
* **Memory**: Prevent retain cycles. Always use `[weak self]` in closures that capture self.
* **Project File**: Keep the `.pbxproj` file clean. Do not manually edit the Xcode project file at first; use `kintsugi`. If the tool cannot solve the issue, edit manually.
* **Actor Isolation**: Default to `@MainActor` for UI components, ViewModels, and UI state models. Only leave the main actor when you intentionally run heavy background compute or I/O.
* **Actor Reentrancy**: Handle reentrancy at `await` suspension points on custom actors by caching in-flight `Task` instances to prevent duplicate concurrent network or disk operations.
* **Protocol Naming**: Follow Apple guidelines by naming ability protocols as adjectives ending in "-able", "-ible", or "-ing.

## 4. Testing Standards
* Organize test methods into clear Arrange, Act, and Assert (AAA) phases with blank lines between them.
* Follow Test-Driven Development (TDD) cycles: Red, Green, Refactor.
* Test business logic and state changes with fast unit tests instead of slow UI tests.
* Declare stored properties in `XCTestCase` as implicitly unwrapped optionals (`!`), initialize in `setUp()`, and set them to `nil` in `tearDown()` (this does not apply to Falabella submodules and the main app, Tottus, and Sodimac). (This doesnt apply for the Falabella sub modules and main app, we use another library for test there)

## 5. CI/CD and Workflows
* Look at `Fastfile` if you need to know the deployment steps.
* Use `bundle exec fastlane` to run lanes.
* Look at `.gitlab-ci.yml` to understand the CI pipeline.
* Look at GitHub workflow or action configuration files to understand the CI pipeline.

## Falabella Project: AI Memory Management

* Write important data to an AI memory file (for example: `ios-browse.md`) every time you complete a task.
* Save all AI memory files in this exact directory: `/Users/alfbaro-mac-pro/Developer/Falabella/`.
* Create the memory file if it does not exist.
* Write technical data that will help you in future tasks. Examples include:
  * Architecture rules or discoveries.
  * Firebase Remote Config changes.
  * Recommendations to refactor code.
* Read these `.md` files at the start of a new session. These files contain your main context. 
* Do not format these files for humans. Format them to maximize your own understanding in future sessions.
