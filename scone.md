# Executor language for the SCONE domains

This file describes the program syntax for the executor implemented in
`strongsup/rlong/executor.py`. This is the executor used in "From Language to
Programs: Bridging Reinforcement Learning and Maximum Marginal Likelihood".

Note #1: the history referencing predicates mentioned in the paper are named
slightly differently in this implementation:
- `prevAction` = `H0`
- `prevArg1` = `H1`
- `prevArg2` = `H2`

Note #2: you may see several files/classes in the project which mention `rlong`.
These are associated with the SCONE dataset, which was created by
**R**eginald **Long**.

## Overview

* World state
  * A **world state** is a list of objects.
  * Each **object** has several properties (colors, position, etc.).
* Logical form
  * Each utterance maps to a single **command**.
  * Each command contains a single **action** and several **arguments**.
  * The arguments are built up before an action is performed.
* Execution
  * The executor processes the logical form from left to right.
  * The executed denotation contains:
    * `world_state` (initialized to a specified initial state)
    * `command_history` (initially an empty list)
    * `utterance_idx` (initially 0)
    * `denotation_stack` (initially an empty stack)
  * Most logical form predicates will modify only the `denotation_stack`.
  * The `world_state`, `command_history`, and `utterance_idx` are modified
    when an action is executed (as explained in the next section)
  * A logical form is terminated when `utterance_idx` exceeds the bound
    of the list of utterances (i.e., `utterance_idx == len(context.utterances)`).
    The finalized denotation is the final `world_state`.

## Predicates and execution

* Primitives
  * The primitives include:
    * Positive numbers: `1`, `2`, `3`, ...
    * Negative numbers: `-1`, `-2`, `-3`, ...
    * Fractions (prefix: X): `X1/1`, `X1/2`, `X3/4`, ...
    * Colors (single char): `r`, `g`, `o`, `y`, `p`, `b`, `e`
  * Execution: Push the primitive onto the stack
  * Examples:
  
    ```
    lf              | stack
    3               | 3
    3 g             | 3 g
    3 g X1/3        | 3 g X1/3
    ```

* Properties (prefix: P): `PColor`, `PShirt`, ...
  * Execution:
    * Pop v from the stack
    * Perform some computation (e.g., look up objects with that property v)
      and push the result onto the stack
  * Examples:
  
    ```
    world_state: 1:g 2: 3:yyy 4:b 5:gg
    lf              | stack
    g               | g
    g PColor        | [1:g, 5:gg]
    ```

* Double-Properties (prefix: D): `DShirtHat`, ...
  * Execution:
    * Pop 2 things from the stack
    * Perform some computation (e.g., look up objects with those 2 property values)
      and push the result onto the stack
  * Examples: (Scene domain)

    ```
    world_state: 1:__ 2:__ 3:__ 4:__ 5:gr 6:__ 7:go 8:__ 9:__ 10:yo
    lf              | stack
    g o             | g o
    g o DShirtHat   | [7:go]
    ```

* `all-objects`
  * Execution: Push the list of all objects onto the stack
  * Examples:
  
    ```
    world_state: 1:g 2: 3:yyy 4:b 5:gg
    lf              | stack
    all-objects     | [1:g, 2:, 3:yyy, 4:b, 5:gg]
    ```

* `index`
  * Execution:
    * Pop a list and a number i (positive or negative) from the stack
    * Push the list member with index i onto the stack
  * Examples:
  
    ```
    world_state: 1:g 2: 3:yyy 4:b 5:gg
    lf                  | stack
    all-objects 4       | [1:g, 2:, 3:yyy, 4:b, 5:gg] 4
    all-objects 4 index | [4:b]
    g PColor            | [1:g, 5:gg]
    g PColor -1         | [1:g, 5:gg] -1
    g PColor -1 index   | [5:gg]
    ```

* Actions (prefix: A): `APour`, `ADrain`, `ARemove`, ...
  * Execution:
    * Pop the action arguments from the stack.
      The action determines the number of arguments.
      Optional requirement: The stack should become empty
    * Apply the action on the world state
    * Save the command (action and arguments) to the command history
    * Increment the utterance count by 1
  * Examples:
  
    ```
    world_state: 1:g 2: 3:yyy 4:b 5:gg
    lf                             | stack
    all-objects 4 index 1          | [4:b] 1
    all-objects 4 index 1 ADrain   | 
        new world_state:     1:g 2: 3:yyy 4: 5:gg
        new command_history: [(Drain, 4:b, 1)]
        new utterance_idx:   1
    ```

* History (prefix: H): `H0`, `H1`, `H2`, ...
  * Execution:
    * Pop a command index i from the stack
    * Look at the ith command history entry.
      If the predicate is `H0`, pull out the action and immediately execute it.
      Otherwise, for predicate `Hj`, pull out the jth argument and push it onto the stack.
        * If it is an object, retrieve the latest attributes for that object
        * If the object has left the scene, then use the attributes that were
        present when the command was executed.
  * Examples:
  
    ```
    (After executing "all-objects 4 index 1 ADrain")
    world_state: 1:g 2: 3:yyy 4: 5:gg
    command_history: [(Drain, 4:b, 1)]
    lf                   | stack
    1 H1                 | 4:b         # 1st argument of the first command
    -1 H2                | 1           # 2nd argument of the last command
    y PColor -1 H2       | [3:yyy] 1
    y PColor -1 H2 -1 H0 |             # Invoke the action of the last command
        new world_state:     1:g 2: 3:yy 4: 5:gg
        new command_history: [(Drain, 4:b, 1), (Drain, 3:yyy 1)]
        new utterance_idx:   2
    ```

## Subdomains

### Alchemy

* World state:
  * 7 beakers
  * Each beaker has up to 4 units of chemical
  * Each unit of chemical has a color (`r`, `g`, `y`, `p`, `o`, `b`)
* Properties:
  * `COLOR PColor`:
    Selects all beakers with a homogeneous content of the specified color.
* Actions:
  * `OBJECT POSITIVE_NUMBER|FRACTION ADrain`:
    Remove the specified amount of chemical from the beaker `OBJECT`
  * `OBJECT1 OBJECT2 APour`:
    Pour all chemical from `OBJECT1` to `OBJECT2`
  * `OBJECT AMix`:
    Mix the chemical in `OBJECT`, making it turn brown (`b`).

### Scene

* World state:
  * A linear stage with 10 slots
  * Each slot may have a single person standing on it
  * Each person has a shirt and optionally a hat.
    Both the shirt and the hat has a color.
  * (Internal) Each person has a hidden ID.
    When `H1`, `H2`, ... is executed,
    the person is retrieved based on the ID.
* Properties:
  * `COLOR PShirt`:
    Selects all people with the specified shirt color
  * `COLOR|e PHat`:
    Selects all people with the specified hat color
  * `OBJECT PLeft`:
    Returns the position to the left of the object
  * `OBJECT PRight`:
    Returns the position to the right of the object
  * `COLOR COLOR|e DShirtHat`:
    Selects all people with the specified shirt and hat color
* Actions:
  * `OBJECT ALeave`:
    Remove the specified person `OBJECT`
  * `OBJECT1 OBJECT2 ASwapHats`:
    Swap the hats of `OBJECT1` and `OBJECT2`
  * `OBJECT NUMBER AMove`:
    Move `OBJECT` to the specified absolute location
  * `NUMBER COLOR COLOR|e ACreate`:
    Create a new person at the specified position, shirt color, and hat color.
    Special: The saved command history is `('Create', person)`

### Tangrams

* World state:
  * A row of tangrams with shape encoded as `0`, `1`, `2`, ...
    The shape, which is also used as a unique ID, cannot be referred to directly.
* Properties:
  * (None)
* Actions:
  * `NUMBER OBJECT AAdd`:
    Insert a tangram to the specified location
  * `OBJECT1 OBJECT2 ASwap`:
    Swap the positions of two tangrams (specified as object or index)
  * `OBJECT ARemove`:
    Remove a tangram (specified as object or index)
