# Debugrithm

### A Python debugging utility with slightly fewer workflow-related inconveniences.

Welcome to **Debugrithm**, a lightweight Python utility for explicit assertion handling, execution tracing, runtime checkpoints, state-based bypassing, and conditional decorator execution.

Debugrithm provides several conveniences:

- **Explicit debugger control** with togglable active and paused execution states.
- **Anonymous and named debuggers** for flexible context tagging.
- **Invasive assertions** through `expectthat()` and `forbidthat()`.
- **Immediate execution halting** through `breakpoint()`.
- **Non-fatal runtime inspection** through `checkpoint()`.
- **Value substitution and state bypassing** through `bypasswith()`.
- **Function invocation tracing** through the `pingcalled()` decorator.
- **Conditional execution and fallbacks** through the `whenproved()` decorator.
- **Structured argument dumping** with timestamps, index tracking, and pretty-printed collections.

Debugrithm intentionally keeps its debugging mechanisms explicit while making execution state and assertion checking straightforward to inspect.

It is designed for programmers who want to trace program flow without repeatedly typing `print(f"HERE {x}")` followed by `exit()`.

Because apparently littering your codebase with unformatted `print()` statements was considered a sophisticated debugging strategy.

---

## 1. Installation

Debugrithm uses Python's standard library and does not require external dependencies.

Import the `Debugger` class from the Debugrithm module.

```python
from debugrithm import Debugger
```

Replace `debugrithm` with the module path used by your installation.

Debugrithm is designed to work with standard Python objects and control flow statements.

---

## 2. Debugger Instantiation

The `Debugger` class serves as the core coordinator for debugging operations.

```python
dbg = Debugger(name="App", used=True)
```

The constructor accepts two optional parameters:

- `name`: A label used in formatted trace headers.
- `used`: A boolean flag determining whether debugging features are active.

By default, `name` is empty (`""`) and `used` is `False`.

```python
dbg = Debugger()
```

When `used` is `False`, the debugger is in a stopped (paused) state, causing debugging operations to act as no-ops.

Because a debugger that cannot be turned off is simply a program that breaks every time you run it.

---

## 3. Anonymous Debuggers

A `Debugger` instance initialized without a `name` parameter (or with `name=""`) functions as an **anonymous debugger**.

```python
dbg = Debugger(used=True)
dbg.checkpoint("Quick check")
```

An anonymous debugger retains full method tracking and timestamping, omitting only the `Name.` prefix in log output headers.

Output:

```text
checkpoint@143000 'Quick check'
```

---

## 4. Debugger State Management

Debugrithm allows enabling or disabling debugging operations dynamically at runtime.

### 4.1 State Queries

Use `running()` and `stopped()` to check the active state of the debugger instance.

| Method | Description | Return Type |
|---|---|---|
| `running()` | Returns `True` if the debugger is active. | `bool` |
| `stopped()` | Returns `True` if the debugger is paused or inactive. | `bool` |

### 4.2 State Modification

The debugger state can be altered at any point using `startit()` and `pauseit()`.

```python
dbg = Debugger(used=True)
dbg.pauseit()
print(dbg.running())

dbg.startit()
print(dbg.running())
```

When paused via `pauseit()`, assertion checks, checkpoints, breakpoints, and traces are completely ignored.

---

## 5. Expecting Conditions: `expectthat`

The `expectthat()` method asserts that a condition must evaluate to `True`.

```python
dbg.expectthat(cond, yes="Condition met", no="Condition failed")
```

### Behavior

- If the debugger is **stopped**, the check is ignored.
- If `bool(cond)` is `True`, Debugrithm outputs the `yes` text and continues execution.
- If `bool(cond)` is `False`, Debugrithm outputs the `no` text and immediately terminates the program via `exit(0)`.

### Example

```python
dbg = Debugger("Auth", used=True)

user_id = 42
dbg.expectthat(user_id > 0, yes="Valid user ID", no="Invalid user ID")
```

Output:

```text
Auth.expectthat@143000 'Valid user ID'
```

---

## 6. Forbidding Conditions: `forbidthat`

The `forbidthat()` method asserts that a condition must evaluate to `False`.

```python
dbg.forbidthat(cond, yes="Not forbidden", no="Forbidden condition occurred")
```

### Behavior

- If the debugger is **stopped**, the check is ignored.
- If `not bool(cond)` is `True`, Debugrithm outputs the `yes` message and continues.
- If `bool(cond)` is `True`, Debugrithm outputs the `no` message and terminates the program via `exit(0)`.

---

## 7. Halting Execution: `breakpoint`

The `breakpoint()` method outputs a formatted diagnostic header along with any positional or keyword arguments, then immediately halts program execution.

```python
dbg = Debugger("Pipeline", used=True)
dbg.breakpoint("Fatal pipeline error", code=500, retries=3)
```

Output:

```text
Pipeline.breakpoint@143000 'Fatal pipeline error'
|0| code=500
|1| retries=3
```

Following the print output, `breakpoint()` calls `exit(0)`.

---

## 8. Non-Fatal Inspection: `checkpoint`

The `checkpoint()` method behaves identically to `breakpoint()` in formatting output, but does **not** terminate program execution.

```python
dbg = Debugger("Worker", used=True)
dbg.checkpoint("Processing items", count=2, items=["a", "b"])
```

Output:

```text
Worker.checkpoint@143000 'Processing items'
|0| count=2
|1| items=
| ['a', 'b']
```

Execution continues uninterrupted after a checkpoint.

A gentle reminder that something happened, without shooting down the entire process.

---

## 9. Value Substitution: `bypasswith`

The `bypasswith()` method allows replacing a default or previous value with a temporary override when debugging is active.

```python
url = dbg.bypasswith("http://localhost:8080", "[https://api.prod.com](https://api.prod.com)", "Overriding API")
```

- If the debugger is **stopped**, returns the previous/original value (`"https://api.prod.com"`).
- If the debugger is **running**, logs the override and returns the new value (`"http://localhost:8080"`).

---

## 10. Function Call Tracing: `pingcalled`

The `pingcalled()` decorator logs when a decorated function is invoked.

```python
@dbg.pingcalled("Calculating total", dump=True)
def calculate(price, tax=0.05):
    return price * (1 + tax)

calculate(100, tax=0.1)
```

Output:

```text
Service.pingcalled@143000 'Calculating total'
|0| 100
|1| tax=0.1
```

Setting `dump=False` logs the function invocation header without printing the parameter values.

---

## 11. Conditional Execution: `whenproved`

The `whenproved()` decorator executes the target function only if a given condition evaluates to `True`.

```python
@dbg.whenproved(is_auth, falb="Denied", yes="Auth OK", no="Auth Failed")
def get_data():
    return "Secret payload"
```

- If **stopped**, the original function executes normally.
- If **running** and `True`, prints `yes` and executes the function.
- If **running** and `False`, prints `no` and returns `falb` without executing the function.

---

## 12. Formatting Mechanics

Debugrithm formats diagnostic output headers through the internal `_indentprint()` helper.

### 12.1 Header Assembly

| Debugger Name | Text | Generated Header Pattern |
|---|---|---|
| `"App"` | `"Loaded"` | `App.checkpoint@143000 'Loaded'` |
| `"App"` | `""` | `App.checkpoint@143000` |
| `""` | `"Loaded"` | `checkpoint@143000 'Loaded'` |

### 12.2 Argument Formatting

Positional and simple keyword arguments are printed with zero-indexed indicators:

```text
|0| 'first_arg'
|1| status=True
```

When keyword arguments contain dictionaries or lists, Debugrithm formats them across multiple lines using Python's `pprint.pformat()` with `width=60`.

```text
|0| data=
| {'items': ['a', 'b', 'c'], 'status': 200}
```

---

## 13. API Summary

### Instantiation & State

```python
Debugger(name="", used=False)
dbg.stopped() -> bool
dbg.running() -> bool
dbg.pauseit() -> None
dbg.startit() -> None
```

### Assertions & Inspection

```python
dbg.expectthat(cond, yes="", no="")
dbg.forbidthat(cond, yes="", no="")
dbg.breakpoint(text="", *args, **kwargs)
dbg.checkpoint(text="", *args, **kwargs)
dbg.bypasswith(curr, prev, text="")
```

### Decorators

```python
@dbg.pingcalled(text="", dump=True)
@dbg.whenproved(cond, falb, yes="", no="")
```

---

## 14. Design Philosophy

Debugrithm is designed as an explicit, low-overhead debugging layer built around simple standard-library utilities.

Rather than running as an interactive debugger attached to a subshell or socket, Debugrithm embeds lightweight assertion and inspection primitives directly into code paths. The library separates operational mechanics cleanly into state control, assertions, fatal/non-fatal inspection, and decorators.

Debugrithm is intentionally compact and relies entirely on Python standard library modules.

The goal is not to replace full-featured interactive debugging suites.

The goal is to make print-debugging structured enough that you aren't embarrassed when someone looks over your shoulder.

---

## 15. Limitations

Debugrithm is intentionally lightweight. The current implementation does not provide:

- Interactive REPL or step-by-step code execution.
- Variable inspection outside of passed arguments.
- Stack trace capture or frame inspection.
- File logging or log level filtering.
- Thread-safe state synchronization.
- Asynchronous (`asyncio`) decorator support.

Program termination via `exit(0)` calls standard system exit routines, which may terminate the entire Python process without throwing catchable standard exceptions.

---

## 16. License

Debugrithm is distributed according to the license included with the project.

See the project's license file for the applicable terms.

---

## 17. Final Example

A compact Debugrithm program demonstrating core formatting and tracing capabilities:

```python
from debugrithm import Debugger

dbg = Debugger("App", used=True)

@dbg.pingcalled("Processing incoming request")
def handle_request(payload):
    dbg.checkpoint("Inspecting payload structure", data=payload)
    dbg.expectthat(len(payload) > 0, yes="Payload is valid", no="Empty payload")

    return dbg.bypasswith("mock_response_200", "real_db_response", "Bypassing DB")

result = handle_request({"user_id": 42, "roles": ["admin", "editor"]})
print(f"Final Result: {result}")
```

### Expected Output

```text
App.pingcalled@143000 'Processing incoming request'
|0| {'roles': ['admin', 'editor'], 'user_id': 42}
App.checkpoint@143000 'Inspecting payload structure'
|0| data=
| {'roles': ['admin', 'editor'], 'user_id': 42}
App.expectthat@143000 'Payload is valid'
App.bypasswith@143000 'Bypassing DB'
Final Result: mock_response_200
```

A small interface for making print-debugging feel like a deliberate software design decision.
