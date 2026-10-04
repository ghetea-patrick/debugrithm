# Debugrithm

> [!CAUTION]
> This README is NOT valid, please wait until this notice is removed to use Debugrithm.

>[!NOTE]
> A note

>[!TIP]
> A tip

>[!IMPORTANT]
> Something important

>[!WARNING]
> A warning

### A Python debugging and flow-control utility with slightly fewer assertion-related inconveniences.

Welcome to **Debugrithm**, a lightweight Python utility for explicit assertion checking, execution tracing, function monitoring, and controlled program termination.

Debugrithm provides a small collection of methods and decorators wrapped inside a `Debugger` class for managing debugging workflows without scattering raw assertion statements and unpredictable `print()` calls throughout your codebase.

Debugrithm provides several conveniences:

- **State management** through `running()`, `stopped()`, `pauseit()`, and `startit()`.
- **Assertion validation** through `expectthat()` for positive conditions.
- **Inverted condition validation** through `forbidthat()` for negative conditions.
- **Hard process termination breakpoints** through `breakpoint()`.
- **Non-fatal execution checkpoints** through `checkpoint()`.
- **Conditional fallback values** through `bypasswith()`.
- **Function call logging decorators** through `pingcalled()`.
- **Conditional function execution decorators** through `whenproved()`.
- **Structured indentation output** formatted with timestamps and inspected arguments.
- **Clean process exit behavior** using standard library mechanisms.

Debugrithm intentionally keeps program debugging explicit while providing readable method names for otherwise noisy control-flow logic.

It is designed for programmers who would rather write:

```python
dbg.expectthat(x > 0, "Valid value", "Value must be positive")
```

than remember which unhandled exception silently corrupted their data three layers deep in an execution loop.

Because naturally software applications prefer leaving mystery clues over clear timestamps and formatted arguments.

---

## 1. Installation

Debugrithm uses Python's standard library and does not require external dependencies.

Import the required class from the Debugrithm module.

```python
from debugrithm import Debugger
```

Replace `debugrithm` with the module path used by your installation.

Debugrithm generates formatted diagnostic messages sent directly to standard output.

---

## 2. Debugger Instantiation

The primary interface for managing diagnostic checks is the `Debugger` class:

```python
dbg = Debugger(name="MainApp", used=True)
```

The constructor accepts an optional label and initial active state.

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `name` | `str` | `""` | Class or subsystem identifier tag |
| `used` | `bool` | `False` | Controls whether diagnostic checks are active |

### Example

```python
dbg = Debugger("Service", used=True)
```

When `used` is set to `False`, all debugging operations and checks are safely bypassed.

---

## 3. State Management

Debugrithm allows inspecting and toggling the active debugging state at runtime.

| Method | Return Type | Description |
|---|---|---|
| `stopped()` | `bool` | Returns `True` if the debugger is currently inactive |
| `running()` | `bool` | Returns `True` if the debugger is currently active |
| `pauseit()` | `None` | Deactivates debugging operations |
| `startit()` | `None` | Activates debugging operations |

### Example

```python
dbg = Debugger("Parser", used=False)

dbg.startit()
print(dbg.running()) # True

dbg.pauseit()
print(dbg.stopped()) # True
```

State methods allow you to selectively enable debugging in specific execution paths without modifying individual assertions.

---

## 4. Expecting Conditions

The `expectthat()` method validates that a given condition evaluates to `True`.

```python
dbg.expectthat(cond, yes="", no="")
```

| Parameter | Type | Purpose |
|---|---|---|
| `cond` | `object` | The condition or expression to evaluate |
| `yes` | `str` | Message printed when the condition is `True` |
| `no` | `str` | Message printed when the condition is `False` |

### Condition Behavior

| Condition Evaluation | Output Action | Execution Result |
|---|---|---|
| `True` | Logs `yes` text | Continues execution |
| `False` | Logs `no` text | Terminates process (`exit(0)`) |

### Example

```python
dbg = Debugger("Auth", used=True)

user_id = 42
dbg.expectthat(user_id > 0, "User ID valid", "Invalid User ID")
```

If the condition fails, Debugrithm prints the failure tag and halts the application immediately.

Programs, like software developers, occasionally need to be explicitly told when a boundary has been crossed.

---

## 5. Forbidding Conditions

The `forbidthat()` method validates that a given condition evaluates to `False`.

```python
dbg.forbidthat(cond, yes="", no="")
```

It operates as the exact inverse of `expectthat()`.

| Condition Evaluation | Output Action | Execution Result |
|---|---|---|
| `False` | Logs `yes` text | Continues execution |
| `True` | Logs `no` text | Terminates process (`exit(0)`) |

### Example

```python
dbg = Debugger("Database", used=True)

is_locked = False
dbg.forbidthat(is_locked, "Database unlocked", "Database is locked")
```

If the forbidden condition evaluates to `True`, the program logs the error message and exits.

---

## 6. Hard Breakpoints

The `breakpoint()` method logs execution details and immediately terminates the program.

```python
dbg.breakpoint(text, *args, **kwargs)
```

Unlike Python's built-in `breakpoint()`, Debugrithm's breakpoint prints formatted inspectable arguments and shuts down process execution cleanly.

### Example

```python
dbg = Debugger("Pipeline", used=True)

dbg.breakpoint("Unreachable state reached", stage="ingest", count=10)
```

Output:

```text
Pipeline.breakpoint@143005 'Unreachable state reached'
|0| stage='ingest'
|1| count=10
```

The application terminates immediately following output generation.

Because continuing process execution after reaching an impossible state is how innocent databases end up with corrupted records.

---

## 7. Execution Checkpoints

The `checkpoint()` method logs diagnostic information without halting execution.

```python
dbg.checkpoint(text, *args, **kwargs)
```

It accepts descriptive text along with arbitrary positional and keyword arguments.

### Example

```python
dbg = Debugger("Worker", used=True)

dbg.checkpoint("Processing batch", 100, status="active")
```

Output:

```text
Worker.checkpoint@143005 'Processing batch'
|0| 100
|1| status='active'
```

Checkpoints allow tracking program progress and state without interrupting workflow execution.

---

## 8. Value Bypassing

The `bypasswith()` method provides conditional value selection based on the debugger state.

```python
value = dbg.bypasswith(curr, prev, text="")
```

| Debugger State | Output Action | Return Value |
|---|---|---|
| `running()` | Logs breakpoint header | Returns `curr` |
| `stopped()` | No output | Returns `prev` |

### Example

```python
dbg = Debugger("Config", used=True)

active_port = dbg.bypasswith(curr=8080, prev=8000, text="Overriding port")
```

Output:

```text
Config.breakpoint@143005 'Overriding port'
```

When active, `bypasswith()` logs the operation and supplies `curr`. When paused, it silently returns `prev`.

---

## 9. Function Call Pinging

The `pingcalled()` decorator wraps functions to monitor invocation events.

```python
@dbg.pingcalled(text="", dump=True)
def my_function():
    ...
```

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `text` | `str` | `""` | Message attached to invocation log |
| `dump` | `bool` | `True` | Controls argument dumping |

### Example

```python
dbg = Debugger("API", used=True)

@dbg.pingcalled("Calculating metrics", dump=True)
def compute(x: int, y: int):
    return x + y

compute(5, 10)
```

Output:

```text
API.pingcalled@143005 'Calculating metrics'
|0| 5
|1| 10
```

If `dump` is set to `False`, Debugrithm logs only the header message without argument breakdown.

---

## 10. Proved Conditions

The `whenproved()` decorator gates function execution based on a condition evaluation.

```python
@dbg.whenproved(cond, falb, yes="", no="")
def my_function():
    ...
```

| Parameter | Type | Purpose |
|---|---|---|
| `cond` | `object` | Condition evaluated upon call |
| `falb` | `object` | Fallback value returned if debugger is stopped |
| `yes` | `str` | Log message when condition evaluates to `True` |
| `no` | `str` | Log message when condition evaluates to `False` |

### Decorator Execution Matrix

| Debugger State | Condition Evaluation | Log Message | Executed Function | Return Value |
|---|---|---|---|---|
| Stopped | N/A | None | No | Returns `falb` |
| Running | `True` | Logs `yes` | Yes | Returns `func()` result |
| Running | `False` | Logs `no` | Yes | Returns `func()` result |

### Example

```python
dbg = Debugger("System", used=True)
ready = True

@dbg.whenproved(ready, falb=None, yes="System ready", no="System degraded")
def execute():
    return "OK"

result = execute()
```

Output:

```text
System.whenproved@143005 'System ready'
```

---

## 11. Output Indentation Mechanics

Debugrithm formats diagnostic logs via an internal `_indentprint()` helper.

Output is formatted into distinct sections:

1. **Header Line:** Contains function identifier, class label, timestamp, and context text.
2. **Positional Arguments:** Displayed with positional index numbers and value representations (`repr`).
3. **Keyword Arguments:** Displayed with key names, index numbers, and values.

```text
[clas.][func]@[HHMMSS] ['text']
|idx| arg
|idx| key=val
```

Timestamps are generated using `strftime("%H%M%S")`.

---

## 12. Dynamic State Control

Debugging checks can be toggled dynamically in long-running loops or high-frequency operations.

```python
dbg = Debugger("Loop", used=False)

for i in range(100):
    if i == 50:
        dbg.startit()
    dbg.checkpoint("Iteration", step=i)
```

This prevents console spam while allowing focused debugging in specific execution windows.

---

## 13. Dictionary and List Formatting

When keyword arguments contain `dict` or `list` instances, Debugrithm formats them using `pprint.pformat()` wrapped at width 60.

```python
dbg = Debugger("Data", used=True)

data = {"status": 200, "items": ["alpha", "beta"]}
dbg.checkpoint("Payload", payload=data)
```

Output:

```text
Data.checkpoint@143005 'Payload'
|0| payload=
| {'items': ['alpha', 'beta'],
| 'status': 200}
```

Multiline structures are indented with leading vertical bars (`|`) for readable terminal scanning.

---

## 14. Program Exit Behavior

When an assertion fails or a breakpoint is reached, Debugrithm exits process execution via `_quitprogram()`.

Under the hood, `_quitprogram()` calls `sys.exit(0)`.

```python
def _quitprogram() -> _Void:
    exit(0)
```

This performs a clean system termination without dumping raw unhandled stack traces to standard error.

---

## 15. Truth Value Evaluation

Conditions supplied to `expectthat()`, `forbidthat()`, and `whenproved()` are explicitly cast using `bool()`.

```python
dbg.expectthat([1, 2], yes="Non-empty list")
dbg.forbidthat([], yes="Empty list verified")
```

Any Python object implementing `__bool__()` or `__len__()` evaluates correctly under these checks.

---

## 16. Decorator Signature Preservation

Decorators in Debugrithm use `functools.wraps`.

```python
@wraps(func)
def wrapper(*args, **kwargs):
    ...
```

This preserves target function metadata including names, docstrings, and type annotations across decorated calls.

---

## 17. Passive Execution When Stopped

When a `Debugger` instance is stopped (`_used = False`), diagnostic operations return immediately.

```python
dbg = Debugger("Passive", used=False)

# Performs no print operations and does not exit
dbg.expectthat(False, no="This will not trigger")
dbg.breakpoint("This will not execute")
```

This design allows debugging infrastructure to remain permanently in source code with zero active console output.

---

## 18. Optional and Empty Parameters

Text messages and argument collections are optional across all Debugrithm methods.

```python
dbg.checkpoint()
dbg.expectthat(True)
```

Output for an unlabelled checkpoint:

```text
checkpoint@143005
```

Omitted labels output minimal headers without unnecessary spacing.

---

## 19. Output Header Construction

The header line produced by `_indentprint()` adapts dynamically based on provided metadata.

```python
_indentprint("checkpoint", "MyClass", "Header text")
```

Result:

```text
MyClass.checkpoint@143005 'Header text'
```

If `clas` is omitted:

```text
checkpoint@143005 'Header text'
```

If `text` is omitted:

```text
MyClass.checkpoint@143005
```

---

## 20. Timestamping Behavior

Timestamps reflect local system time at the moment of method execution.

Format specification:

```text
HHMMSS
```

Example: `143005` represents `14:30:05` (2:30:05 PM).

This allows chronological sorting of terminal outputs during asynchronous or multi-step execution tracing.

---

## 21. Complete Example: Basic Flow Control

The following example demonstrates assertions, checkpoints, and conditional verification.

```python
from debugrithm import Debugger

dbg = Debugger("AppModule", used=True)

# Log checkpoint
dbg.checkpoint("Initializing sub-systems", status="OK")

# Validate expectations
config_loaded = True
dbg.expectthat(config_loaded, yes="Configuration loaded", no="Config missing")

# Verify forbidden states
has_errors = False
dbg.forbidthat(has_errors, yes="No runtime errors detected", no="Errors found")
```

Output:

```text
AppModule.checkpoint@143005 'Initializing sub-systems'
|0| status='OK'
AppModule.expectthat@143005 'Configuration loaded'
AppModule.forbidthat@143005 'No runtime errors detected'
```

---

## 22. Complete Example: Function Monitoring

The following example demonstrates function call inspection using decorators.

```python
from debugrithm import Debugger

dbg = Debugger("Services", used=True)

@dbg.pingcalled("User login handler", dump=True)
def login(username: str, roles: list):
    return f"Logged in {username}"

login("admin", ["read", "write"])
```

Output:

```text
Services.pingcalled@143005 'User login handler'
|0| 'admin'
|1| roles=
| ['read', 'write']
```

---

## 23. Complete Example: Dynamic State Toggling

The following example demonstrates enabling and disabling debugging during runtime operations.

```python
from debugrithm import Debugger

dbg = Debugger("BatchProcessor", used=False)

items = ["item1", "item2", "item3"]

for item in items:
    if item == "item2":
        dbg.startit()
    
    dbg.checkpoint("Processing item", item=item)
    
    dbg.pauseit()
```

Output:

```text
BatchProcessor.checkpoint@143005 'Processing item'
|0| item='item2'
```

Only `item2` outputs diagnostic telemetry because debugging was paused for all other iterations.

---

## 24. API Summary

### Debugger Class Constructor

```python
Debugger(name: str = "", used: bool = False)
```

### State Inspection and Control

```python
Debugger.stopped() -> bool
Debugger.running() -> bool
Debugger.pauseit() -> None
Debugger.startit() -> None
```

### Assertion and Validation Methods

```python
Debugger.expectthat(cond: object, yes: str = "", no: str = "") -> None
Debugger.forbidthat(cond: object, yes: str = "", no: str = "") -> None
```

### Execution Control Methods

```python
Debugger.breakpoint(text: str = "", *args, **kwargs) -> None
Debugger.checkpoint(text: str = "", *args, **kwargs) -> None
Debugger.bypasswith(curr: object, prev: object, text: str = "") -> object
```

### Function Decorators

```python
Debugger.pingcalled(text: str = "", dump: bool = True) -> Callable
Debugger.whenproved(cond: object, falb: object, yes: str = "", no: str = "") -> Callable
```

---

## 25. Design Philosophy

Debugrithm is designed to provide a readable Python interface for explicit program diagnostics and runtime assertion checks.

The library deliberately wraps debugging primitives inside explicit method names rather than relying on standard `assert` statements, which can be optimized away with Python's `-O` flag.

The architecture separates debugging functionality into logical operations:

- `expectthat` handles positive assertions.
- `forbidthat` handles negative assertions.
- `breakpoint` handles process termination upon state failure.
- `checkpoint` handles non-fatal state output.
- `bypasswith` handles runtime value fallbacks.
- `pingcalled` handles function call telemetry.
- `whenproved` handles conditional function execution.

Debugrithm does not attempt to replace full logging frameworks or interactive step-through debuggers like `pdb`.

It simply makes diagnostic logging and flow-control assertions less unpleasant to write.

Which, frankly, is already a respectable contribution to civilization.

---

## 26. Limitations

Debugrithm is intentionally lightweight and currently provides a focused set of debugging capabilities.

The current implementation does not provide:

- Multi-destination log routing (file, socket, or stream handlers).
- Log severity levels (DEBUG, INFO, WARN, ERROR).
- Asynchronous function decorator hooks.
- Interactive terminal REPL debugging.
- Automated stack trace generation.
- Thread-safe state locks for concurrent access.
- Structured JSON or XML export formatting.
- Integration with standard library `logging` handlers.

The library outputs directly to standard stdout using `print()`.

---

## 27. Final Example

A compact Debugrithm program can look like this:

```python
from debugrithm import Debugger

dbg = Debugger("Main", used=True)

@dbg.pingcalled("Execution start")
def run_task(task_id: int):
    dbg.expectthat(task_id > 0, "Valid task ID", "Invalid task ID")
    dbg.checkpoint("Task running", task_id=task_id)

run_task(101)
```

Output:

```text
Main.pingcalled@143005 'Execution start'
|0| 101
Main.expectthat@143005 'Valid task ID'
Main.checkpoint@143005 'Task running'
|0| task_id=101
```

The runtime handles application execution while Debugrithm formats diagnostic tracing.

Debugrithm simply provides names for the machinery.

Because apparently scattering `print("HERE 1")` statements throughout a codebase was considered a perfectly reasonable user interface.
