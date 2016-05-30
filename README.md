# BWBGT

A simple Python background task processor using [pickle](https://docs.python.org/2/library/pickle.html) and [os.fork()](https://docs.python.org/2/library/os.html#os.fork)

## Example:

```python
import bwbgt
from time import sleep
```

So we have a function that takes a while to return something
```python
def long_task(arg1, arg2):
    sleep(5)
    return 'Long task with args %s, %s ended!' % (arg1, arg2)
```

This function will add a task and run it, then do some other stuff until it's ready, removing it after printing the result
```python
def test_run():
    task_id = bwbgt.add_task(long_task, ['myarg1', 'myarg2'])
    bwbgt.run_task(task_id)
    print 'Task %s started...' % task_id

    # Do stuff while task is running
    for _ in range(10):
        print 'Stuff while task is running %i' % (_+1)
        sleep(0.1)

    while True: # Keep waiting for the task to complete
        # Do some more stuff while waiting
        print 'Waiting for task to be ready...'
        sleep(0.5)
        if bwbgt.task_ready(task_id):
            break

    task_details = bwbgt.task_details(task_id)

    print 'It took %i seconds for the task to return %s' % (
        task_details['end_time']-task_details['start_time'],
        task_details['result']
    )

    bwbgt.remove_task(task_id)


test_run()
```
