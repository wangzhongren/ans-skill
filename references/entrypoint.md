# Application Entry and Lifecycle

Use with role-card.md's Required reading. These rules retain the global mutation and architectural boundaries.

### Root Application Entry File

Place the application startup file at the project root; the layer directories may live under `src/` according to the accepted layout. For JavaScript use root `main.js`; for other languages choose the corresponding entry filename, such as `main.py`, `main.go`, or `main.cpp`, using the project's language and toolchain. Here, "main" denotes this startup responsibility, not a mandatory JavaScript extension. If a toolchain requires a different physical location, report that constraint and agree on the layout rather than silently relocating the requested root entry. It is a thin process bootstrap, not a sixth architectural layer or a global dependency container. Implement it after the required Interface is available. For startup failures, begin investigation here before tracing down the operational chain:

```text
root application entry -> Interface -> Pipeline -> Service -> Provider
```

- **Bootstrap inputs:** Obtain minimal startup options from process arguments, environment, or an explicitly supplied configuration object, validate required options, and pass plain values to the Interface startup operation. Direct process argument/environment access here is limited to bootstrap configuration; runtime business configuration, file loading, secrets retrieval, database access, and network clients remain Provider responsibilities through the adjacent-layer chain.
- **Start:** Invoke the designated Interface startup operation, await readiness, and retain only its public lifecycle handle. Do not import or construct Pipeline, Service, or Provider directly, select their concrete implementations, scan their folders for auto-registration, or hold their capability objects. Each layer manages its own immediate dependencies.
- **Stop:** Register applicable process termination handlers, request shutdown through the Interface lifecycle handle, and await bounded cleanup before exiting. Make shutdown safe to request more than once. Interface and the lower layers release the resources they own through adjacent-layer lifecycle operations; main must not close lower-layer clients directly.
- **Failure reporting:** Handle startup and fatal boundary failures, report a concise diagnostic without exposing secrets, set an appropriate nonzero exit status, and request cleanup of any successfully started Interface. Do not silently swallow failures or put business retries, request handlers, data transformations, or workflow orchestration in main. Process lifecycle controls and terminal startup diagnostics are bootstrap duties; they do not authorize other infrastructure work here.
- **Load and link safety:** Separate callable startup from executable invocation using the project's language conventions. Loading or linking startup code for tests must not start listeners, initialize resources, register process handlers, or exit the process. Application modules must not import main; dependency direction begins at main and points into Interface.
- **Verification:** Add startup tests under `test/main/` or the established equivalent. With a controlled Interface, verify valid startup options and readiness, rejection of invalid options, startup failure and exit status, bounded graceful shutdown, repeated termination requests, and import safety as applicable. Run an isolated smoke test using the actual start command before declaring startup complete. Main tests supplement the five layer suites; record commands and results under the same evidence rules.

For an existing application, identify its actual executable entry and include any requested rename or startup-script change in the Mutation Contract rather than creating a competing entry point. This skill describes the required application structure; do not add an empty application entry file to the skill package itself.
