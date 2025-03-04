import storage
import supervisor

storage.remount("/", False)
supervisor.set_next_stack_limit(4096 + 4096)
