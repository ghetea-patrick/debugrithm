# Debugrithm

**Print-debugging, with a name tag and an off switch.**

Debugrithm is a lightweight Python utility for explicit assertions, execution tracing, runtime checkpoints, value overrides, and conditional decorators. You put the debugging operations directly in your code and decide when they are active.

If your current debugging strategy is `print(f"HERE {x}")` followed by `exit()`, this gives that workflow a little structure. The detective work is still yours; at least the evidence gets a timestamp.

[What it does](#what-it-does) · [Get started](#get-started) · [A quick example](#a-quick-example) · [How it fits together](#how-it-fits-together) · [Reference](#reference) · [Examples](#examples) · [Good to know](#good-to-know) · [Design notes](#design-notes)

## What it does

- Creates named or anonymous `Debugger` instances for tagging diagnostic output.
- Switches debugging on and off with explicit running and paused states.
- Checks expected and forbidden conditions through `expectthat()` and `forbidthat()`.
- Prints diagnostics and stops execution through `breakpoint()`.
- Prints the same style of diagnostics while continuing execution through `checkpoint()`.
- Substitutes temporary values with `bypasswith()` while debugging is active.
- Traces function calls with `pingcalled()` and optionally dumps their arguments.
- Gates decorated functions with `whenproved()`, including a fallback return value.
- Formats output with method names, timestamps, zero-based argument indices, and pretty-printed collections.

## Get started

> [!NOTE]
> Debugrithm uses only Python's standard library and works with ordinary Python objects and control flow. Replace the module path below if your installation uses a different one.

```python
from debugrithm import Debugger
```

Create a debugger and turn it on explicitly:

```python
dbg = Debugger(name="App", used=True)
```

The constructor accepts two optional arguments:

| Argument | Default | Purpose |
| --- | --- | --- |
| `name` | `""` | Label included in formatted trace headers. |
| `used` | `False` | Whether the debugging features start active. |

With no arguments, the debugger starts stopped:

```python
dbg = Debugger()
```

> [!IMPORTANT]
> `Debugger()` is inactive by default. Use `used=True` or call `startit()` when you want debugging output and checks. Pausing disables the debugging behavior; decorated application functions still follow the paused behavior documented below.

## A quick example

An anonymous debugger is useful for a quick inspection:

```python
dbg = Debugger(used=True)
dbg.checkpoint("Quick check")
```

Illustrative output:

```text
checkpoint@143000 'Quick check'
```

You still get the method name and timestamp. Leaving `name` empty only removes the `Name.` prefix from the header; it does not remove tracking or timestamping.

> [!NOTE]
> The examples use `143000` as a sample timestamp. Your output reflects the time of the actual call.

## How it fits together

### Query the current state

Use these methods whenever you need to know whether an instance is active:

| Method | Description | Return Type |
|---|---|---|
| `running()` | Returns `True` if the debugger is active. | `bool` |
| `stopped()` | Returns `True` if the debugger is paused or inactive. | `bool` |

### Start and pause debugging

You can change the state at runtime:

```python
dbg = Debugger(used=True)
dbg.pauseit()
print(dbg.running())

dbg.startit()
print(dbg.running())
```

The two `print()` calls produce `False` and then `True`. While paused, assertion checks, checkpoints, breakpoints, and trace output are ignored.

### Choose what should happen at a debugging point

| Operation | Running behavior | Stopped behavior |
| --- | --- | --- |
| `expectthat(cond, ...)` | Log success if `bool(cond)` is true; log failure and call `exit(0)` otherwise. | Ignore the check. |
| `forbidthat(cond, ...)` | Log success if `bool(cond)` is false; log failure and call `exit(0)` otherwise. | Ignore the check. |
| `breakpoint(...)` | Print the diagnostics and call `exit(0)`. | Ignore the debugging operation. |
| `checkpoint(...)` | Print the diagnostics and continue. | Ignore the debugging operation. |
| `bypasswith(curr, prev, ...)` | Log the override and return `curr`. | Return `prev`. |
| `pingcalled(...)` | Log the call, optionally dump arguments, and invoke the function. | Invoke the function normally without tracing. |
| `whenproved(cond, falb, ...)` | Run the function when the condition is true; otherwise return `falb`. | Run the original function normally. |

The distinction matters most for the decorators: turning debugging off restores normal execution rather than making the decorated function disappear.

## Reference

### Require a true condition: `expectthat()`

Use `expectthat()` when a condition must be truthy:

```python
dbg.expectthat(cond, yes="Condition met", no="Condition failed")
```

- If the debugger is stopped, it ignores the check.
- If `bool(cond)` is `True`, it prints `yes` and continues.
- If `bool(cond)` is `False`, it prints `no` and immediately calls `exit(0)`.

For example:

```python
dbg = Debugger("Auth", used=True)

user_id = 42
dbg.expectthat(user_id > 0, yes="Valid user ID", no="Invalid user ID")
```

Output:

```text
Auth.expectthat@143000 'Valid user ID'
```

### Require a false condition: `forbidthat()`

Use `forbidthat()` when a condition must be falsy:

```python
dbg.forbidthat(cond, yes="Not forbidden", no="Forbidden condition occurred")
```

- If the debugger is stopped, it ignores the check.
- If `not bool(cond)` is `True`, it prints `yes` and continues.
- If `bool(cond)` is `True`, it prints `no` and calls `exit(0)`.

Here, `yes` means the check passed: the forbidden condition did **not** occur. `no` reports that it did occur.

> [!CAUTION]
> These are invasive checks. A failed active check ends execution through `exit(0)`, and the exit status is **zero**, even on failure. Treat that as debugging behavior when interpreting a script's result in a shell or automation system.

### Print and stop: `breakpoint()`

An active `breakpoint()` prints a diagnostic header, positional arguments, and keyword arguments, then halts execution:

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

After printing, it calls `exit(0)`. This method is Debugrithm's print-and-stop operation; it does not open an interactive debugging session.

### Print and continue: `checkpoint()`

`checkpoint()` uses the same output formatting while allowing the program to continue:

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

Execution continues immediately after the checkpoint. Sometimes you need a breadcrumb, not a shutdown sequence.

### Substitute a value: `bypasswith()`

Use a temporary override when debugging is running and retain the original value when it is stopped:

```python
url = dbg.bypasswith("http://localhost:8080", "https://api.prod.com", "Overriding API")
```

| State | Returned value | Diagnostic output |
| --- | --- | --- |
| Stopped | Previous/original value: `"https://api.prod.com"`. | No override trace. |
| Running | Current override: `"http://localhost:8080"`. | Logs `"Overriding API"`. |

The argument order is `curr`, then `prev`, then optional text. The first value is the debugging substitute; the second is the value you use during normal execution.

### Trace a function call: `pingcalled()`

The decorator logs each invocation of the decorated function. This example uses a debugger named `Service`:

```python
dbg = Debugger("Service", used=True)
```

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

With `dump=True`, the trace includes parameter values. Set `dump=False` to keep the invocation header while omitting the argument dump.

### Gate a function: `whenproved()`

This decorator selects between calling the function and returning a fallback:

```python
@dbg.whenproved(is_auth, falb="Denied", yes="Auth OK", no="Auth Failed")
def get_data():
    return "Secret payload"
```

`is_auth` is the condition supplied by your application. The state and condition determine the result:

| State | Condition | Result |
| --- | --- | --- |
| Stopped | Either value. | Execute the original function normally. |
| Running | True. | Print `yes`, then execute the function. |
| Running | False. | Print `no`, then return `falb` without executing the function. |

In this example, the active false branch returns `"Denied"`; the true branch runs `get_data()` and returns `"Secret payload"`.

### Understand the diagnostic format

The internal `_indentprint()` helper assembles diagnostic headers. The debugger name, method, timestamp, and optional text are combined like this:

| Debugger Name | Text | Generated Header Pattern |
|---|---|---|
| `"App"` | `"Loaded"` | `App.checkpoint@143000 'Loaded'` |
| `"App"` | `""` | `App.checkpoint@143000` |
| `""` | `"Loaded"` | `checkpoint@143000 'Loaded'` |

An empty message omits the quoted text. An empty debugger name omits the name and its trailing dot.

Positional arguments and simple keyword arguments use zero-based indices:

```text
|0| 'first_arg'
|1| status=True
```

Dictionary and list values passed as keyword arguments use multiple lines, formatted with Python's `pprint.pformat()` using `width=60`:

```text
|0| data=
| {'items': ['a', 'b', 'c'], 'status': 200}
```

That gives larger values some breathing room without making you format each collection by hand.

### API at a glance

The signatures below collect the constructor, state methods, inspection methods, and decorators in one place. Return annotations describe the interface.

#### Instantiation & State

```text
Debugger(name="", used=False)
dbg.stopped() -> bool
dbg.running() -> bool
dbg.pauseit() -> None
dbg.startit() -> None
```

#### Assertions & Inspection

```text
dbg.expectthat(cond, yes="", no="")
dbg.forbidthat(cond, yes="", no="")
dbg.breakpoint(text="", *args, **kwargs)
dbg.checkpoint(text="", *args, **kwargs)
dbg.bypasswith(curr, prev, text="")
```

#### Decorators

```text
@dbg.pingcalled(text="", dump=True)
@dbg.whenproved(cond, falb, yes="", no="")
```

## Examples

### Trace a request from entry to result

This combines invocation tracing, a structured checkpoint, an assertion, and a debugging override:

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

Expected output, using the illustrative timestamp:

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

The call is traced first, the payload is inspected next, and the nonempty-payload check passes. Because the debugger is active, `bypasswith()` returns `"mock_response_200"` instead of `"real_db_response"`.

## Good to know

Debugrithm stays focused on explicit inspection inside your own code. The current implementation does not provide:

- An interactive REPL or step-by-step execution.
- Variable inspection beyond the arguments you pass in.
- Stack-trace capture or frame inspection.
- File logging or log-level filtering.
- Thread-safe state synchronization.
- Asynchronous (`asyncio`) decorator support.

> [!IMPORTANT]
> In ordinary Python execution, `exit(0)` raises `SystemExit`. It can terminate the process if it propagates, and it is not caught by `except Exception` because `SystemExit` derives from `BaseException`. Catching `SystemExit` explicitly is possible. The stop operations are still intended to end execution.

Use the running/stopped state deliberately: a paused debugger skips its assertions, returns original values from `bypasswith()`, and lets decorated functions execute normally. Those choices are part of the interface, not a replacement for your application's own validation or control flow.

## Design notes

Debugrithm embeds small assertion and inspection primitives directly into code paths. State control, assertions, fatal and non-fatal inspection, value substitution, and decorators each have a clear role, built with standard-library utilities and little overhead.

It stays compact instead of attaching an interactive debugger through a subshell or socket. The aim is to make print-debugging deliberate, readable, and easy to turn off. Your future self deserves better than twelve identical lines saying `HERE`.
