import supervisor  # circuitpython module will need stub/mock for IDE intellesense, Issue #27

supervisor.set_next_stack_limit(4096 + 4096)
